# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

import os
import re
import shutil
import signal
import sys
import threading
import time
import typing as t
from _collections_abc import Iterable
from abc import abstractmethod, ABCMeta
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from functools import lru_cache
from math import ceil
from time import sleep
from typing import overload

import psutil
import pytermor as pt
import readchar
from pytermor import FT
from readchar import key, config

from es7s import APP_VERSION
from es7s.cli._base import get_current_command_name
from es7s.shared import with_terminal_state
from es7s.shared import (
    Styles as BaseStyles,
    get_stdout,
    FrozenStyle,
    ShutdownableThread,
    IoProxy,
    get_logger,
)
from es7s.shared import TerminalState
from es7s.shared import IoInterceptor, make_interceptor_io
from es7s.shared import exit_gracefully
from .._base_opts_params import CMDTRAIT_ADAPTIVE, CMDTYPE_BUILTIN
from .._decorators import (
    catch_and_log_and_exit,
    cli_command,
    cli_argument,
)


@cli_command(
    __file__,
    type=CMDTYPE_BUILTIN,
    traits=[CMDTRAIT_ADAPTIVE],
    short_help="&(auto)-process-&(term)inator",
)
@cli_argument(
    "filter",
    nargs=1,
    default="^xb.+",
)
@catch_and_log_and_exit
class invoker:
    """
    Evolution of es7s/pgrek, which supported only one fixed filter,
    without a possibility to alter it unless restarted. This one
    [...]
    """

    def __init__(self, filter: str, **kwargs):
        self._main = Autoterm(filter, interval_sec=0.5)
        self._run()

    def _run(self):
        self._main.run()


@dataclass(frozen=True)
class JournalRecord:
    event: str = "Event"
    pid: int = None
    details: str = None
    important: bool = False
    ts: int = field(default_factory=time.time_ns)

    @property
    def header_style(self) -> pt.Style:
        if self.important:
            return AutotermStyles.HEADER_JOURNAL_IM
        return AutotermStyles.HEADER_JOURNAL

    @property
    def table_style(self) -> pt.Style:
        if self.important:
            return AutotermStyles.TABLE_JOURNAL_IM
        return AutotermStyles.TABLE_JOURNAL

    def dt(self) -> datetime:
        return datetime.fromtimestamp(self.ts / 1e9)

    def compose(self) -> str:
        return f'{pt.fit(self.event, 20)} [{self.pid}] "{self.details}"'

    def compose_brief(self) -> str:
        return f"{self.event}" + (f" [{self.pid}]" if self.pid else "")


class Journal(deque[JournalRecord]):
    def last_msg(self) -> JournalRecord | str:
        if len(self):
            return self.__getitem__(0)
        return "journal is empty"

    @overload
    def write(self, event: str, details: str, important=False):
        ...

    @overload
    def write(self, event: str, pinfo: "ProcessInfo", important=False):
        ...

    def write(self, event: str, arg, important=False):
        if isinstance(arg, ProcessInfo):
            jr = JournalRecord(
                event,
                arg.pid,
                details=" ".join(arg.cmdline),
                important=important,
            )
        else:
            jr = JournalRecord(event, details=str(arg), important=important)

        self.appendleft(jr)

    def write_filter_update(self, filter: str):
        self.write("Filter update", f"Filter set to: {filter!r}")


class NextTick(Exception):
    pass


class InputCancelled(Exception):
    pass


class NoTargetError(Exception):
    pass


class ForbiddenAction(Exception):
    timeout_sec = 5


class InvalidActionKey(Exception):
    ticks = 1

    def __init__(self, key: str):
        super().__init__(f"Unbound key: {key!r}")


class DisallowedAction(Exception):
    ticks = 1

    def __init__(self) -> None:
        super().__init__(f"Action is not available in the current mode")


class StatusMessage:
    DEFAULT_TIMEOUT_SEC = 2

    def __init__(self, msg: str, timeout_sec: int = None):
        self.msg: str = msg
        self.label: str = "×"
        self.timeout_sec: int = timeout_sec or self.DEFAULT_TIMEOUT_SEC

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, StatusMessage):
            return False
        return self.msg == o.msg

    def __repr__(self) -> str:
        return f"<{pt.get_qname(self)}>[{self.timeout_sec}, {pt.cut(self.msg, 40)}]"

    @classmethod
    def make(cls, e: Exception) -> "StatusMessage":
        timeout_sec = getattr(e, "timeout_sec", None)
        return cls(str(e), timeout_sec)


class AutotermDynColor(pt.DynamicColor[FrozenStyle]):
    STYLE_MAP = {
        "default": FrozenStyle(fg=pt.cv.SKY_BLUE_2, bg=pt.cv.NAVY_BLUE),
        "auto": FrozenStyle(fg=pt.cv.INDIAN_RED_1, bg=pt.cv.DARK_RED),
        "help": FrozenStyle(fg=pt.cvr.SEA_FOAM_GREEN, bg=pt.cvr.DARK_GREEN),
    }

    @classmethod
    @overload
    def update(cls, ctx: "AutotermContext" = None) -> None:
        ...

    @classmethod
    def update(cls, **kwargs) -> None:
        super().update(**kwargs)

    @classmethod
    def _update_impl(cls, ctx: "AutotermContext" = None) -> FrozenStyle:
        if not ctx:
            return cls.STYLE_MAP.get("default")

        state_name = ctx.state.name
        key = state_name
        if state_name not in cls.STYLE_MAP.keys():
            key = "default"
        if ctx.auto_enabled:
            key = "auto"
        return cls.STYLE_MAP.get(key)


_DYNAMIC_FG = AutotermDynColor("fg")
_DYNAMIC_BG = AutotermDynColor("bg")


class AutoLoopStyles(BaseStyles):
    STATUS_BG = pt.NOOP_COLOR
    STATUS_ERROR_BG = pt.cv.DARK_RED
    STATUS_ERROR_LABEL_BG = pt.cv.RED

    ACTION_KEY = FrozenStyle(bg=pt.cv.GRAY_23, fg=pt.cv.GRAY_100, bold=True)
    ACTION_KEY_DISABLED = FrozenStyle(ACTION_KEY, bg=pt.DEFAULT_COLOR, fg=pt.cv.GRAY_35)
    ACTION_KEY_PUSHED = FrozenStyle(bg=pt.cv.GRAY_11, fg=_DYNAMIC_FG, blink=True)
    SC_ACTION_KEY_INACTIVE = FrozenStyle(ACTION_KEY, bg=pt.cv.GRAY_23)
    SC_ACTION_KEY_ACTIVE = FrozenStyle(ACTION_KEY, bg=pt.cv.GRAY_0)

    ACTION_NAME = FrozenStyle(bg=pt.cv.GRAY_11)
    ACTION_NAME_DISABLED = FrozenStyle(bg=pt.DEFAULT_COLOR, fg=pt.cv.GRAY_35)
    ACTION_NAME_PUSHED = FrozenStyle(ACTION_NAME, fg=_DYNAMIC_FG, blink=True)
    SC_ACTION_NAME_INACTIVE = FrozenStyle(bg=pt.cv.GRAY_3)
    SC_ACTION_NAME_ACTIVE = FrozenStyle(fg=pt.cv.GRAY_100)


ActionFn = t.TypeVar("ActionFn", bound=t.Callable[["AutoContext"], None])
ActionBFn = t.TypeVar("ActionBFn", bound=t.Callable[["AutoContext"], bool])
NOOP_FN = lambda *_: None


class AutoState:
    def __init__(self, name: str = "noop", exec_fn: ActionFn = NOOP_FN):
        self._name: str = name
        self._exec_fn: ActionFn = exec_fn

    @property
    def name(self) -> str:
        return self._name

    def exec_fn(self, ctx: "AutoContext"):
        return self._exec_fn(ctx)

    def __repr__(self):
        return f"<{pt.get_qname(self)}[{self._name} {self._exec_fn}]>"


class AutoContext:
    def __init__(self, ui: "ThreadUi"):
        self.action_keymap = dict[str, AutoAction]()
        self.action_groups = dict[str, AutoGroup]()
        self.action_queue = deque[AutoAction]()

        self._ui: "ThreadUi" = ui
        self.termstate: TerminalState = None  # noqa

        self.tick: int = 0
        self.state: AutoState = AutoState()

    @property
    def ui(self) -> "ThreadUi":
        return self._ui


_AT = t.TypeVar("_AT", bound="AutoAction")


class AutoGroup(t.Generic[_AT], deque[_AT]):
    def __init__(self, name: str):
        super().__init__()
        self.name = name


class AutoAction:
    def __init__(
        self,
        name: str,
        groups: list,
        exec_fn: ActionFn = None,
        prereq_fn: ActionBFn = None,
        visibility_fn: ActionBFn = None,
    ):
        self._name: str = name
        self._groups: list[AutoGroup] = groups
        self._exec_fn: ActionFn = exec_fn or (lambda *_: None)
        self._prereq_fn: ActionBFn = prereq_fn or (lambda *_: True)
        self._visibility_fn: ActionBFn = visibility_fn or (lambda *_: True)

        self.keys: list[str] = []
        for grp in self._groups:
            grp.append(self)

    def name(self, ctx: "AutoContext") -> str:
        return self._name

    def exec_fn(self, ctx: "AutoContext"):
        return self._exec_fn(ctx)

    def prereq_fn(self, ctx: "AutoContext") -> bool:
        return self._prereq_fn(ctx)

    def visibility_fn(self, ctx: "AutoContext") -> bool:
        return self._visibility_fn(ctx)

    def format_hint(self, ctx: AutoContext) -> t.Iterable[pt.RT]:
        action_st_key, action_st_name = self._get_hint_styles(ctx)
        action_name = self.name(ctx)

        if self.keys:
            yield AdaptiveFragment(1, f" {self.keys[0]} ", action_st_key)
        yield AdaptiveFragment(5, f" {action_name}  ", action_st_name)

    def _get_hint_styles(self, ctx: AutoContext) -> tuple[pt.Style, pt.Style]:
        if not self.prereq_fn(ctx):
            return AutoLoopStyles.ACTION_KEY_DISABLED, AutoLoopStyles.ACTION_NAME_DISABLED
        return AutoLoopStyles.ACTION_KEY, AutoLoopStyles.ACTION_NAME


class KeyExistsError(Exception):
    pass


class AALoopBase(metaclass=ABCMeta):  # Automaton Multi-Threaeded Altmode
    def __init__(self, context: AutoContext = None):
        if not context:
            context = AutoContext(ThreadUi())
        self._input_timeout_sec = 1.0
        self._ctx: AutoContext = context

    def _make_action_group(self, name: str) -> AutoGroup:
        if self.ctx.action_groups.get(name, None):
            raise KeyExistsError(name)
        autogroup = self.ctx.action_groups[name] = AutoGroup(name)
        return autogroup

    def _bind_action(self, keys: str | list[str], action: AutoAction) -> AutoAction:
        if isinstance(keys, str):
            keys = [keys]
        for key in keys:
            if not key:
                continue
            if key in self.ctx.action_keymap.keys():
                raise KeyExistsError(key)
            self.ctx.action_keymap.update({key: action})
            action.keys.append(key)
        return action

    @property
    def ctx(self) -> AutoContext:
        return self._ctx

    @with_terminal_state(alt_buffer=True, no_cursor=True)
    def run(self, termstate: TerminalState):
        self._ctx.termstate = termstate
        self._init_input_mode()
        self._main()

    @abstractmethod
    def _init_input_mode(self):
        raise NotImplementedError

    def _main(self):
        while True:
            self.ctx.tick += 1

            if self.ctx.action_queue:
                action = self.ctx.action_queue.pop()

                if action.prereq_fn(self.ctx):
                    try:
                        action.exec_fn(self._ctx)
                    except (ForbiddenAction, NoTargetError) as e:
                        self.ctx.ui.add_status(e)
                    except NextTick:
                        continue
                    except (StopIteration, KeyboardInterrupt):
                        break

            self._ctx.state.exec_fn(self._ctx)

            try:
                self._wait_key()
            except KeyboardInterrupt:
                break

        self._on_shutdown()
        exit_gracefully(2)

    def _wait_stdin(self, timeout: float) -> None | t.TextIO:
        import select

        i, _, _ = select.select([sys.stdin], [], [], timeout)
        if not i:
            return None
        return sys.stdin

    def _wait_key(self):
        if stdin := self._wait_stdin(self._input_timeout_sec):
            inp = self._read_key(stdin)
            # if inp != "\n":
            #    inp = inp.rstrip("\n")
            try:
                self._on_key_press(inp)
            except InvalidActionKey as e:
                self.ctx.ui.add_status(e)

    @abstractmethod
    def _wait_input(self) -> str:
        pass

    @abstractmethod
    def _read_key(self, stream: t.IO) -> str:
        raise NotImplementedError

    @abstractmethod
    def _on_input(self, inp: str):
        raise NotImplementedError

    def _on_key_press(self, key: str):
        if not (action := self.ctx.action_keymap.get(key, None)):
            if not (action := self.ctx.action_keymap.get(key.rstrip(), None)):  # for debugger
                raise InvalidActionKey(key)
        get_logger().debug(f"Key pressed: [{key}]")
        self.ctx.action_queue.append(action)

    def _on_shutdown(self):
        pass


class AALoopDiscreteInput(AALoopBase, metaclass=ABCMeta):
    def _init_input_mode(self):
        self._ctx.termstate.discrete_input()

    def _wait_input(self, maxlen: int = None) -> str:
        queue = deque(maxlen=maxlen)
        stdout = get_stdout()

        while True:
            if k := self._read_key(sys.stdin):
                if k in [key.BACKSPACE, key.DELETE]:
                    continue
                if k in [key.ENTER]:
                    break
                if set(k) == {key.ESC}:
                    raise InputCancelled
                if k.isprintable():
                    if len(queue) == queue.maxlen:
                        continue
                    queue.append(k)
                    stdout.io.write(k)
                    stdout.io.flush()

        return "".join(queue)

    def _key_to_keyname(self, key: str):
        for keyname in dir(readchar._posix_key):
            if getattr(readchar._posix_key, keyname, None) == key:
                return keyname
        return key

    def _read_key(self, stream: t.IO) -> str:
        c1 = stream.read(1)
        if c1 in config.INTERRUPT_KEYS:
            raise KeyboardInterrupt
        if c1 != "\x1B":
            return c1

        c2 = stream.read(1)
        if c2 not in "\x4F\x5B":
            return c1 + c2

        c3 = stream.read(1)
        if c3 not in "\x31\x32\x33\x35\x36":
            return c1 + c2 + c3

        c4 = stream.read(1)
        if c4 not in "\x30\x31\x33\x34\x35\x37\x38\x39":
            return c1 + c2 + c3 + c4

        c5 = stream.read(1)
        return c1 + c2 + c3 + c4 + c5


class AALoopToggleInput(AALoopBase, metaclass=ABCMeta):
    def _init_input_mode(self):
        self._ctx.termstate.disable_input()

    def _wait_input(self):
        self._input_mode(True)
        try:
            if stdin := self._wait_stdin(30):
                self._on_input(stdin.readline(-1).strip() or "")
        finally:
            self._input_mode(False)

    def _read_key(self, stream: t.IO) -> str:
        return stream.read(1)[0]

    def _input_mode(self, enable: bool):
        termstate = self._ctx.termstate
        if enable:
            termstate.show_cursor()
            termstate.restore_input()
        else:
            termstate.hide_cursor()
            termstate.disable_input()


class ThreadUi(ShutdownableThread):
    def __init__(self):
        super().__init__(command_name=get_current_command_name(), thread_name="ui", daemon=True)
        self.buffer_lock = threading.RLock()
        self.echo_lock = threading.Lock()
        self._update_required = threading.Event()

        self._origin: IoProxy = get_stdout()
        self._buffer: IoInterceptor = make_interceptor_io()

    def _postflush(self):
        pass

    def add_status(self, payload: str | StatusMessage | Exception):
        pass

    def _update_status(self):
        pass

    def flush(self):
        if not self._update_required.is_set():
            return

        with self.buffer_lock:
            buf_val = self._buffer.popvalue()
            # buf_val = buf_val.replace(" ", "␣")
        with self.echo_lock:
            self._origin.echo(pt.make_clear_display().assemble(), nl=False)
            self._origin.echo(pt.make_reset_cursor().assemble(), nl=False)
            self._origin.echo(buf_val, nl=False)
            self._postflush()

        self._update_status()
        self._update_required.clear()

    def _get_status_line_fill(self, error: bool, line: int = 1, column: int = 1) -> str:
        col = AutoLoopStyles.STATUS_ERROR_BG if error else AutoLoopStyles.STATUS_BG
        return self._get_line_fill(col, line, column)

    def _get_header_line_fill(self, st: pt.Style, line: int = 1, column: int = 1) -> str:
        return self._get_line_fill(st.bg, line, column)

    def _get_line_fill(self, col: pt.Color, line: int, column: int = 1) -> str:
        if line <= 0:
            line = self.term_height + line
        if column <= 0:
            column = self.term_width + column
        return pt.term.compose_clear_line_fill_bg(col.to_sgr(pt.ColorTarget.BG), line, column)

    def becho(self, string: str | pt.ISequence = "", *, nl=False):
        with self.buffer_lock:
            self._buffer.echo(string, nl=nl)
        self._update_required.set()

    @t.overload
    def becho_rendered(self, inp: str, style: pt.Style, *, nl=False) -> None:
        ...

    @t.overload
    def becho_rendered(self, inp: str | pt.IRenderable, *, nl=False) -> None:
        ...

    def becho_rendered(self, *args, nl=False) -> None:
        with self.buffer_lock:
            self._buffer.echo_rendered(*args, nl=nl)
        self._update_required.set()

    def echo_now(self, string: str | pt.ISequence = "", *, nl=False):
        self._origin.echo(string, nl=nl)

    def render(self, string: pt.RT | list[pt.RT] = "", fmt: pt.FT = pt.NOOP_STYLE) -> str:
        return self._buffer.render(string, fmt)

    @property
    def term_width(self) -> int:
        return pt.get_terminal_width(pad=0)

    @property
    def term_height(self) -> int:
        return shutil.get_terminal_size().lines


# ----------------------------------------------------------------------------------------


class AutotermContext(AutoContext):
    PROMPT_TOO_MANY_PROCESSES = 10
    MAX_FILTER_LENGTH = 32

    def __init__(self, ui: "ThreadUiAT", filter: str):
        super().__init__(ui)
        self._ui.ctx = self

        self.action_group_states: AutoGroup[StateChangeAction] = None  # noqa
        self.action_group_actions: AutoGroup = None  # noqa
        self.filter = filter
        self.no_partial_update = threading.Event()
        self.no_partial_update.set()
        self.journal_enabled = False
        self.help_enabled = False
        self.auto_enabled = False

        self.proc_obsolete = threading.Event()
        self.proc_obsolete.set()
        self.proc_updating = threading.Lock()
        self.proc_updating_write = threading.Lock()

        self.proc_shown = list[ProcessInfo]()
        self.proc_filtered: int = 0

        self.journal = Journal()
        self.journal.write_filter_update(self.filter)
        self.help = Help()

    @property
    def ui(self) -> "ThreadUiAT":
        return t.cast(ThreadUiAT, self._ui)


@dataclass
class ProcessInfo:
    pid: int
    name: str
    cmdline: str
    username: str

    cpu_percent: float = 0.0
    memory: float = 0.0
    running: bool = True

    created_at: float = field(default_factory=time.time_ns)
    dead_at: float = 0.0

    process: psutil.Process = None
    matches: list[re.Match | None] = field(init=False)
    pending_signal: signal.Signals = None
    error: Exception = None

    @staticmethod
    def match(regex: re.Pattern[str], *fields: str | None) -> list[re.Match | None]:
        fields = [*filter(None, fields)]
        return [*map(regex.search, fields)]

    @staticmethod
    def sort(instance: "ProcessInfo") -> float:
        return -instance.cpu_percent

    def refresh(self) -> bool:
        if not self.running:
            return False
        try:
            with self.process.oneshot():
                self.cpu_percent = self.process.cpu_percent()
                self.memory = self.process.memory_full_info()[0]
        except psutil.AccessDenied as e:
            self.error = e
        except psutil.NoSuchProcess:
            self.dead_at = time.time_ns()
            self.running = False
            return True
        return False


class StateChangeAction(AutoAction):
    def __init__(
        self,
        state: AutoState,
        cb: t.Callable,
        name: str,
        groups: list,
        visibility_fn: ActionBFn = None,
    ):
        super().__init__(name, groups, self.exec_fn, self.prereq_fn, visibility_fn)
        self.state = state
        self._cb = cb
        self.style = AutotermDynColor.STYLE_MAP.get(name)

    def exec_fn(self, ctx: AutoContext):
        self._cb(self.state)

    def prereq_fn(self, ctx: AutoContext) -> bool:
        return ctx.state != self.state

    def _get_hint_styles(self, ctx: AutoContext) -> tuple[pt.Style, pt.Style]:
        if ctx.state != self.state:
            return (
                AutoLoopStyles.SC_ACTION_KEY_INACTIVE,
                AutoLoopStyles.SC_ACTION_NAME_INACTIVE,
            )

        return (
            FrozenStyle(
                AutoLoopStyles.SC_ACTION_KEY_ACTIVE,
                fg=_DYNAMIC_BG,
                bg=_DYNAMIC_FG,
                dim=True,
                inversed=True,
            ),
            FrozenStyle(AutoLoopStyles.SC_ACTION_NAME_ACTIVE, fg=_DYNAMIC_FG, bg=_DYNAMIC_BG),
        )


class KillAction(AutoAction):
    def __init__(self, name: str, groups: list, exec_fn: ActionFn):
        super().__init__(name, groups, exec_fn, self.prereq_fn)

    def prereq_fn(self, ctx: AutoContext) -> bool:
        if ctx.state.name not in ["proclist", "journal"]:
            return False
        if t.cast(AutotermContext, ctx).auto_enabled:
            return False
        return True


class ToggleAction(AutoAction):
    def __init__(
        self,
        name: str,
        groups: list,
        exec_fn: ActionFn = None,
        prereq_fn: ActionBFn = None,
        visibility_fn: ActionBFn = None,
        value_fn: ActionBFn = None,
        active_st: pt.Style = pt.NOOP_STYLE,
    ):
        super().__init__(name, groups, exec_fn, prereq_fn, visibility_fn)
        self.value_fn = value_fn
        self.active_st = active_st

    def _get_hint_styles(self, ctx: AutoContext) -> tuple[pt.Style, pt.Style]:
        if self.value_fn(ctx):
            return AutoLoopStyles.ACTION_KEY_PUSHED, AutoLoopStyles.ACTION_NAME_PUSHED
        return super()._get_hint_styles(ctx)


class Help(dict[str, str]):
    def __init__(self):
        super().__init__(
            {
                "proclist": "Show list of processes that match the filter",
                "journal": "Show event log",
                "help": "Show this page",
                "edit": "Change current filter (regexp)",
                "term1": "Send SIGTERM to the first visible process in the list",
                "termall": "Send SIGTERM to ALL visible processes in the list",
                "autoterm": "Enable automatic mode -- the app will send SIGTERM to currently visible processes and any new ones that will be detected further",
                "kill1": "Send SIGKILL to the first visible process in the list",
                "killall": "Send SIGKILL to ALL visible processes in the list",
                "exit": "Close the application",
            }
        )


class Autoterm(AALoopDiscreteInput):
    def __init__(self, filter: str, interval_sec: float):
        self._th_ui = ThreadUiAT()
        super().__init__(AutotermContext(self._th_ui, filter))
        self._input_timeout_sec = interval_sec

        self._state_proclist = AutoState("proclist", self._state_proclist_fn)
        self._state_journal = AutoState("journal", self._state_journal_fn)
        self._state_help = AutoState("help", self._state_help_fn)

        self.ctx.action_group_states = gs = self._make_action_group("states")
        self.ctx.action_group_actions = ga = self._make_action_group("actions")

        csfn = self._change_state
        self._bind_action("p", StateChangeAction(self._state_proclist, csfn, "proclist", [gs]))
        self._bind_action("j", StateChangeAction(self._state_journal, csfn, "journal", [gs]))
        self._bind_action("h", StateChangeAction(self._state_help, csfn, "help", [gs]))
        self._bind_action(
            ["e", "=", "\n"],
            AutoAction("edit", [ga], self._action_edit_fn, lambda ctx: not ctx.auto_enabled),
        )
        self._bind_action("t", KillAction("term1", [ga], self._action_term_fn))
        self._bind_action("T", KillAction("termall", [ga], self._action_term_all_fn))
        self._bind_action(
            "A",
            ToggleAction(
                "autoterm",
                [ga],
                exec_fn=self._action_toggle_auto_fn,
                prereq_fn=lambda ctx: ctx.state.name in ["proclist", "journal"],
                value_fn=lambda ctx: ctx.auto_enabled,
                active_st=AutotermDynColor.STYLE_MAP["auto"],
            ),
        )
        self._bind_action("k", KillAction("kill1", [ga], self._action_kill_fn))
        self._bind_action("K", KillAction("killall", [ga], self._action_kill_all_fn))
        self._bind_action("q", AutoAction("exit", [ga], self._action_exit_fn))

        self._th_reader = ThreadReader(self.ctx)
        self._th_killer = ThreadKiller(self.ctx)

        self._change_state(self._state_proclist)
        self._th_ui.start()
        self._th_reader.start()
        self._th_killer.start()

    @property
    def ctx(self) -> AutotermContext:
        return t.cast(AutotermContext, self._ctx)

    def _main(self):
        super()._main()
        self._th_killer.join()
        self._th_reader.join()
        self._th_ui.join()

    def _change_state(self, new_state: AutoState):
        get_logger().debug(f"Changing state to: {new_state!r}")
        ctx = self.ctx
        ctx.state = new_state
        ctx.journal_enabled = ctx.state == self._state_journal
        ctx.help_enabled = ctx.state == self._state_help
        if ctx.help_enabled:
            ctx.auto_enabled = False
        AutotermDynColor.update(ctx=ctx)

    def _on_input(self, inp: str | None):
        ctx = self.ctx

        ctx.ui.echo_now(pt.SeqIndex.RESET)
        if inp and self._validate_filter(inp):
            get_logger().debug(f"Input received: {inp!r}")
            ctx.filter = inp
            ctx.journal.write_filter_update(ctx.filter)
            ctx.proc_obsolete.set()

    def _on_shutdown(self):
        self.ctx.ui.echo_shutting_down()
        self.ctx.no_partial_update.set()

    def _action_help_fn(self, _):
        self._change_state(self._state_help)

    def _action_back_fn(self, _):
        self._change_state(self._state_proclist)

    def _action_edit_fn(self, _):
        ctx = self.ctx

        try:
            ctx.no_partial_update.set()
            ctx.termstate.show_cursor()
            ctx.ui.echo_prompt()
            inp = self._wait_input(32)
            self._on_input(inp)
        except InputCancelled:
            self._on_input(None)
        finally:
            ctx.termstate.hide_cursor()
            ctx.no_partial_update.clear()

    def _action_exit_fn(self, _):
        raise StopIteration

    def _action_term_fn(self, _):
        if self._validate_current_filter(check_amount=False):
            self._th_killer.kill()

    def _action_term_all_fn(self, _):
        if self._validate_current_filter():
            self._th_killer.kill(all=True)

    def _action_kill_fn(self, _):
        if self._validate_current_filter(check_amount=False):
            self._th_killer.kill(sig=signal.SIGKILL)

    def _action_kill_all_fn(self, _):
        if self._validate_current_filter():
            self._th_killer.kill(all=True, sig=signal.SIGKILL)

    def _state_help_fn(self, _):
        ctx = self.ctx

        with ctx.ui.buffer_lock:
            ctx.ui.bufecho_header()
            ctx.ui.bufecho_filter()
            ctx.ui.bufecho_help()
            ctx.ui.bufecho_footer()
            self._refresh_processes()
            ctx.ui.flush()

    def _state_proclist_fn(self, _):
        ctx = self.ctx

        if ctx.auto_enabled:
            self._th_killer.kill(all=True, auto=True)

        with ctx.ui.buffer_lock:
            ctx.ui.bufecho_header()
            ctx.ui.bufecho_footer()

            if self.ctx.proc_updating_write.acquire(timeout=0):
                ctx.ui.bufecho_filter()
                ctx.ui.bufecho_proclist()
                self._refresh_processes()
                self.ctx.proc_updating_write.release()
                self.ctx.no_partial_update.clear()

            ctx.ui.flush()

    def _state_journal_fn(self, _):
        ctx = self.ctx

        if ctx.auto_enabled:
            self._th_killer.kill(all=True, auto=True)

        with ctx.ui.buffer_lock:
            ctx.ui.bufecho_header()
            ctx.ui.bufecho_footer()

            if self.ctx.proc_updating_write.acquire(timeout=0):
                ctx.ui.bufecho_filter()
                ctx.ui.bufecho_jounral()
                self._refresh_processes()
                self.ctx.proc_updating_write.release()
                self.ctx.no_partial_update.clear()

            ctx.ui.flush()

    def _action_toggle_auto_fn(self, _):
        ctx = self.ctx

        if not ctx.auto_enabled:
            if not self._validate_current_filter():
                return
        ctx.auto_enabled = not ctx.auto_enabled
        AutotermDynColor.update(ctx=ctx)

    def _validate_current_filter(self, check_amount: bool = True) -> bool:
        ctx = self.ctx

        if not self._validate_filter(ctx.filter):
            return False

        if check_amount and len(ctx.proc_shown) >= ctx.PROMPT_TOO_MANY_PROCESSES:
            return self._prompt_yn()
        return True

    def _validate_filter(self, filterval: str) -> bool:
        if len(filterval) <= 2:
            raise ForbiddenAction("For safety reasons filters required to be at least 3 chars long")
        try:
            re.compile(filterval)
        except Exception as e:
            raise ForbiddenAction(f"Entered filter is not a valid regex: {e!s}")
        return True

    def _refresh_processes(self):
        for p in self.ctx.proc_shown:
            if p.refresh():
                if p.pending_signal:
                    self.ctx.journal.write("Terminated", p)
                else:
                    self.ctx.journal.write("Disappeared", p)

    def _prompt_yn(self) -> bool:
        ctx = self.ctx

        try:
            ctx.no_partial_update.set()
            ctx.ui.echo_prompt_yn()
            if stdin := self._wait_stdin(10):
                inp = self._read_key(stdin)
                return inp in ["y", "Y"]
        except InputCancelled:
            return False
        finally:
            ctx.no_partial_update.clear()
            ctx.ui.echo_now(pt.SeqIndex.RESET)

        return False


class ThreadReader(ShutdownableThread):
    def __init__(self, ctx: AutotermContext):
        super().__init__(
            command_name=get_current_command_name(), thread_name="preader", daemon=True
        )
        self._ctx = ctx
        self._interval_sec = 1.0

        self._pinfos = dict[int, ProcessInfo]()
        self._last_filter: str | None = None

    @property
    def ctx(self) -> AutotermContext:
        return t.cast(AutotermContext, self._ctx)

    def run(self):
        super().run()

        while True:
            if self.is_shutting_down():
                self.destroy()
                return

            with self.ctx.proc_updating:
                self.ctx.ui.echo_activity_indic()
                self._read(re.compile(self.ctx.filter))
            self.ctx.ui.echo_activity_indic()

            sleep(self._interval_sec)

    def _read(self, current_filter: re.Pattern[str]):
        shown = []
        filtered = 0

        if current_filter != self._last_filter:
            self._pinfos.clear()

        for p in psutil.process_iter(["pid", "name", "cmdline", "username"]):
            pdata = t.cast(dict, getattr(p, 'info'))
            if not pdata["cmdline"] or p.pid == self.self_pid():  # ignore self, ignore threads
                continue

            matches = ProcessInfo.match(current_filter, pdata["name"], " ".join(pdata["cmdline"]))
            if not any(matches):
                filtered += 1
                continue
            pinfo = self._pinfos.get(p.pid, None)
            if not pinfo:
                pinfo = ProcessInfo(**p.info)  # noqa
                pinfo.process = p
                pinfo.matches = matches
                self._pinfos.update({p.pid: pinfo})
                self.ctx.journal.write("New match", pinfo)

        for pid in [*self._pinfos.keys()]:
            pinfo = self._pinfos[pid]
            if not pinfo.running and (time.time_ns() - pinfo.dead_at) / 1e9 > 5.0:
                del self._pinfos[pid]
                continue
            shown.append(pinfo)

        shown = sorted(shown, key=ProcessInfo.sort)
        self._last_filter = current_filter
        # if self.ctx.proc_ids == pids:
        #     self.ctx.proc_obsolete.clear()
        #     return

        with self.ctx.proc_updating_write:
            self.ctx.proc_shown = shown
            self.ctx.proc_filtered = filtered
            self.ctx.proc_obsolete.clear()

    @lru_cache
    def self_pid(self):
        return os.getpid()


class ThreadKiller(ShutdownableThread):
    def __init__(self, ctx: AutotermContext):
        super().__init__(
            command_name=get_current_command_name(), thread_name="pkiller", daemon=True
        )
        self._ctx = ctx
        self._interval_sec = 0.5

        self._killing_queue = deque[tuple[ProcessInfo, signal.Signals]]()

    @property
    def ctx(self) -> AutotermContext:
        return t.cast(AutotermContext, self._ctx)

    def kill(self, all=False, sig=signal.SIGTERM, auto: bool = False):
        with self.ctx.proc_updating:
            if not len(self.ctx.proc_shown) and not auto:
                raise NoTargetError("No valid targets")
            for pinfo in self.ctx.proc_shown:
                if pinfo.pending_signal:
                    continue
                pinfo.pending_signal = sig
                self._killing_queue.append((pinfo, sig))
                mode = "Auto" if auto else "Manual"
                self.ctx.journal.write(f"Queued ({mode})", pinfo)
                if not all:
                    break

    def run(self):
        super().run()

        while True:
            if self.is_shutting_down():
                self.destroy()
                return

            while len(self._killing_queue):
                self.ctx.proc_updating_write.acquire()
                pinfo, sig = self._killing_queue.popleft()
                try:
                    proc = psutil.Process(pinfo.pid)
                    proc.send_signal(sig)
                    self.ctx.journal.write(f"Sent {sig.name}", pinfo, important=True)
                    if proc:
                        proc.wait(1)
                except Exception as e:
                    self.ctx.journal.write(f"Error: {pt.get_qname(e)}", pinfo, important=True)

                self.ctx.proc_updating_write.release()

            time.sleep(self._interval_sec)


class AutotermStyles(AutoLoopStyles):
    # fmt: off
    HEADER =                 FrozenStyle(                     bg=_DYNAMIC_BG)
    HEADER_FILTER_CHAR =     FrozenStyle(fg=_DYNAMIC_FG,      bg=_DYNAMIC_BG, bold=True)
    HEADER_FILTER =          FrozenStyle(fg=pt.cv.YELLOW,     bg=_DYNAMIC_BG, bold=True)
    HEADER_NUM =             FrozenStyle(fg=pt.cv.GRAY,       bg=_DYNAMIC_BG, bold=True)
    HEADER_NUM_ACTIVE =      FrozenStyle(fg=pt.cvr.AIR_SUPERIORITY_BLUE,
                                         bg=_DYNAMIC_BG, bold=True)
    HEADER_NUM_CAUTION =     FrozenStyle(fg=pt.cv.HI_RED,     bg=_DYNAMIC_BG, bold=True)
    HEADER_NUM_OBSOLETE =    FrozenStyle(fg=pt.cv.GRAY_42,    bg=_DYNAMIC_BG, bold=True)
    HEADER_LABEL =           FrozenStyle(fg=pt.cv.GRAY,       bg=_DYNAMIC_BG)
    HEADER_JOURNAL =         FrozenStyle(fg=pt.cv.GRAY_42,    bg=_DYNAMIC_BG)
    HEADER_JOURNAL_IM =      FrozenStyle(fg=_DYNAMIC_FG,      bg=_DYNAMIC_BG)
    HEADER_QUESTION =        FrozenStyle(fg=pt.cv.GOLD_2,     bg=_DYNAMIC_BG, bold=True)
    HEADER_QUESTION_PROMPT = FrozenStyle(fg=pt.cv.GRAY_0,     bg=pt.cv.GOLD_2, bold=True)
    HEADER_QUESTION_YN =     FrozenStyle(HEADER_QUESTION,     blink=True)
    HEADER_EDIT =            FrozenStyle(fg=pt.cv.GRAY_0,     bg=pt.cv.YELLOW, bold=True)
    HEADER_EDIT_PROMPT =     FrozenStyle(fg=pt.cv.YELLOW,     bg=_DYNAMIC_BG, bold=True, blink=True)
    HEADER_VERSION =         FrozenStyle(fg=pt.cv.GRAY_35)

    IRQ_INDICATOR =          FrozenStyle(fg=_DYNAMIC_FG)

    TABLE_PROC =             FrozenStyle()
    TABLE_PROC_OBSOLETE =    FrozenStyle(fg=pt.cv.GRAY_42)
    TABLE_PROC_TERMINATING = FrozenStyle(fg=pt.cv.RED,        bold=True)
    TABLE_PROC_KILLING =     FrozenStyle(fg=pt.cv.HI_RED,     bold=True)
    TABLE_PROC_DEAD =        FrozenStyle(fg=pt.cv.HI_RED,     bg=pt.cv.DARK_RED_2)

    TABLE_JOURNAL =          FrozenStyle()
    TABLE_JOURNAL_IM =       FrozenStyle(fg=_DYNAMIC_FG,      bold=True)

    HELP_HINT_COLOR =        pt.cvr.MINT_GREEN
    HELP_HINT_NAME =         FrozenStyle(fg=HELP_HINT_COLOR,  bold=True)
    HELP_HINT_LABEL =        FrozenStyle(fg=pt.cv.GRAY_0,     bg=AutotermDynColor.STYLE_MAP['help'].bg, bold=True)
    HELP_HINT_ICON =         FrozenStyle(fg=HELP_HINT_COLOR,  bold=True, blink=True)

    EXIT_LABEL =             FrozenStyle(fg=pt.cv.GRAY_0,     bg=pt.cvr.SAFETY_YELLOW, bold=True)
    EXIT =                   FrozenStyle(fg=pt.cvr.SAFETY_YELLOW,
                                         bg=_DYNAMIC_BG, bold=True)
    # fmt: on


_Styles = AutotermStyles


class ThreadUiAT(ThreadUi):
    MODES_ROWNUM = 1
    FILTER_ROWNUM = 2
    PROMPT_ROWNUM = 2
    SHUTDOWN_ROWNUM = 2
    ACTIONS_ROWNUM = 0  # bottom
    STATUS_ROWNUM = 2
    CONTENT_ROWNUM = 3
    ACTIVITY_INDIC_ROWNUM = 2
    ACTIVITY_INDIC_COLNUM = 1

    def __init__(self):
        super().__init__()
        self.ctx: AutotermContext = None  # noqa
        self.status_lock = threading.Lock()
        self._interval_sec = 1.0

        self._status_queue = deque[StatusMessage]()
        self._prev_status_update_ts = 0

        self._formatter_mem = pt.StaticFormatter(
            auto_color=False,
            allow_negative=False,
            discrete_input=True,
            unit_separator="",
            pad=False,
        )

    def run(self):
        super().run()

        while True:
            if self.is_shutting_down():
                self.destroy()
                return

            if not self.ctx.no_partial_update.is_set():
                self._update_status()
            sleep(self._interval_sec)

    def _postflush(self):
        self.echo_activity_indic()

    def add_status(self, payload: str | StatusMessage | Exception):
        if isinstance(payload, str):
            sm = StatusMessage(payload)
        elif isinstance(payload, Exception):
            sm = StatusMessage.make(payload)
            self._origin.echo("\a", nl=True)
        else:
            sm = payload

        if sm in self._status_queue:
            return
        with self.status_lock:
            self._status_queue.append(sm)

    def echo_activity_indic(self, active: bool = None):
        if self.ctx.no_partial_update.is_set():
            return

        if active is None:
            active = self.ctx.proc_updating.locked()

        s = "·" if active else " "
        coords = (self.ACTIVITY_INDIC_ROWNUM, self.ACTIVITY_INDIC_COLNUM)
        self._origin.echo_rendered(
            pt.make_save_cursor_position().assemble()
            + pt.make_set_cursor(*coords).assemble()
            + s
            + pt.make_restore_cursor_position().assemble(),
            pt.merge_styles(AutotermStyles.HEADER, overwrites=[_Styles.IRQ_INDICATOR]),
            nl=False,
        )

    def echo_prompt(self):
        prompt_st_1 = self._get_header_line_fill(_Styles.HEADER, self.PROMPT_ROWNUM)
        prompt_lpad = pt.Fragment("", _Styles.HEADER_EDIT)
        prompt_label = pt.Fragment(" > ", _Styles.HEADER_EDIT_PROMPT)
        prompt_input = pt.Fragment(
            self._get_header_line_fill(
                _Styles.HEADER_EDIT, self.PROMPT_ROWNUM, 1 + len(prompt_lpad) + len(prompt_label)
            )
        )
        prompt_savecur = pt.make_save_cursor_position().assemble()
        # prompt_input_sgr = (
        #     pt.Fragment("\x00", _Styles.HEADER_EDIT).render(get_stdout().renderer).split("\x00")[0]
        # )
        prompt_input_sgr = pt.Fragment(" " * (self.ctx.MAX_FILTER_LENGTH + 2), _Styles.HEADER_EDIT)
        prompt_st_2 = self._get_header_line_fill(
            _Styles.HEADER,
            self.PROMPT_ROWNUM,
            1 + len(prompt_lpad) + len(prompt_label) + len(prompt_input_sgr),
        )
        prompt_restcur = pt.make_restore_cursor_position().assemble()
        prompt_input_empty = (
            pt.Fragment("\x00", _Styles.HEADER_EDIT).render(get_stdout().renderer).split("\x00")[0]
        )
        prompt = (
            prompt_st_1
            + prompt_lpad
            + prompt_label
            + " "
            + prompt_savecur
            + prompt_input
            + prompt_input_sgr
            + prompt_st_2
            + prompt_restcur
            + prompt_input_empty
        )

        self._origin.echo_rendered(prompt, nl=False)

    def echo_prompt_yn(self):
        prompt_st_1 = self._get_header_line_fill(_Styles.HEADER_QUESTION, self.PROMPT_ROWNUM)
        prompt_icon = pt.Fragment(" ? ", _Styles.HEADER_QUESTION_PROMPT)
        prompt_label = pt.Fragment(
            f" {len(self.ctx.proc_shown)} processes will be affected, continue? ",
            _Styles.HEADER_QUESTION,
        )
        prompt_prompt = pt.Fragment(" (y/n) ", _Styles.HEADER_QUESTION_YN)
        self._origin.echo_rendered(
            prompt_st_1 + prompt_icon + prompt_label + prompt_prompt, nl=False
        )

    def echo_shutting_down(self):
        if self.ctx.no_partial_update.is_set():
            return

        msg = (
            self._get_line_fill(AutotermStyles.EXIT.bg, self.SHUTDOWN_ROWNUM)
            + self.render(" ! ", AutotermStyles.EXIT_LABEL)
            + self.render(" Shutting down", AutotermStyles.EXIT)
        )
        self.echo_now(msg)

    def _update_status(self):
        if not len(self._status_queue):
            return

        with self.status_lock:
            msg = self._status_queue[0]
            msg.timeout_sec -= self._set_prev_status_update_ts()
            if msg.timeout_sec <= 0:
                self._status_queue.remove(msg)

        with self.echo_lock:
            self._echo_status(msg)

    def _echo_status(self, msg: StatusMessage):
        status_text = pt.Text(
            self._get_status_line_fill(True, self.STATUS_ROWNUM),
            pt.Fragment(
                f" {msg.label} ",
                pt.Style(fg=pt.cv.HI_WHITE, bg=AutoLoopStyles.STATUS_ERROR_LABEL_BG, bold=True),
            )
            + pt.Fragment(
                pt.cut(" Error: " + msg.msg, self.term_width - 3 - len(msg.label)),
                pt.Style(bg=AutoLoopStyles.STATUS_ERROR_BG),
            ),
            pt.SeqIndex.RESET.assemble(),
        )
        self._origin.echo_rendered(status_text, nl=False)
        self._set_prev_status_update_ts()

    def _set_prev_status_update_ts(self) -> float:
        tdelta = (now := datetime.now().timestamp()) - self._prev_status_update_ts
        if self._prev_status_update_ts == 0:
            tdelta = self._interval_sec
        self._prev_status_update_ts = now
        return tdelta

    def bufecho_proclist(self):
        cursor_y = self.CONTENT_ROWNUM
        obsolete = self.ctx.proc_obsolete.is_set()

        def override_st() -> pt.Style:
            if obsolete:
                return _Styles.TABLE_PROC_OBSOLETE
            if not p.running:
                return _Styles.TABLE_PROC_DEAD
            if p.pending_signal:
                if p.pending_signal == signal.SIGKILL:
                    return _Styles.TABLE_PROC_KILLING
                return _Styles.TABLE_PROC_TERMINATING
            return pt.NOOP_STYLE

        def highlight(s: str, pid: bool = False):
            if ov_st := override_st():
                if pid:
                    ov_st = pt.Style(ov_st, crosslined=True)
                return pt.Fragment(s, ov_st)
            return pt.highlight(s)

        self.becho(pt.make_set_cursor(cursor_y, 1))

        if obsolete or not len(self.ctx.proc_shown):
            if obsolete:
                self.becho_rendered(f"working..{(self.ctx.tick % 2)*'.'}", _Styles.TEXT_DEFAULT)
            else:
                self.becho_rendered("nothing to show", _Styles.TEXT_LABEL)
            return

        for p in self.ctx.proc_shown:
            generic_st = _Styles.TABLE_PROC
            if ov_st := override_st():
                generic_st = ov_st

            if generic_st.bg not in [pt.NOOP_COLOR, pt.DEFAULT_COLOR]:
                pfill = (
                    generic_st.bg.to_sgr(pt.ColorTarget.BG).assemble()
                    + pt.make_clear_line_after_cursor().assemble()
                )
                self.becho_rendered(pfill)
            sep = pt.Fragment("  ", generic_st)

            pid = highlight(f"{p.pid:8d}", pid=True)
            # unix process names are cut to 15 chars :(
            pname = self._highlight_match(p, p.name, 14, p.matches[0], generic_st)
            pcpu = (
                highlight(pt.format_auto_float(p.cpu_percent, 3))
                if p.running
                else pt.Fragment(" " * 3, generic_st)
            )
            pmem = highlight(pt.fit(self._formatter_mem.format(p.memory), 5, ">"))
            puser = pt.Fragment(pt.fit(p.username, 10), generic_st)
            psig = ""
            if p.pending_signal:
                psig = sep + pt.Fragment(
                    p.pending_signal.name, FrozenStyle(override_st(), crosslined=False)
                )
            pcmd = self._highlight_match(
                p, " ".join(p.cmdline), self.term_width - 51 - len(psig), p.matches[1], generic_st
            )
            pline = pt.Composite(pid, sep, pname, sep, pcpu, sep, pmem, sep, puser, sep, pcmd, psig)

            self.becho(pt.make_set_cursor(cursor_y, 1))
            self.becho_rendered(pline)
            cursor_y += 1
            if cursor_y >= self.term_height:
                break

    def bufecho_jounral(self):
        cursor_y = self.CONTENT_ROWNUM
        sep = pt.Fragment("  ")

        if not len(self.ctx.journal):
            self.becho_rendered(str(self.ctx.journal.last_msg()), _Styles.TEXT_LABEL)
            return

        reduce = 0
        if self.term_width < 80:
            dt_format = "%H:%M:%S"
        elif self.term_width < 120:
            dt_format = "%H:%M:%S.%f"
            reduce = -3
        elif self.term_width < 160:
            dt_format = "%0e-%b %H:%M:%S.%f"
            reduce = -3
        else:
            dt_format = "%0e-%b %H:%M:%S.%f"

        for jr in self.ctx.journal:
            generic_st = jr.table_style
            timestr = jr.dt().strftime(dt_format)
            if reduce:
                timestr = timestr[:reduce]
            time = pt.Fragment(timestr, AutotermStyles.TABLE_JOURNAL)
            msg = pt.Fragment(
                pt.fit(jr.compose(), self.term_width - len(time) - len(sep)), generic_st
            )
            jrline = pt.Text(time + sep + msg)

            self.becho(pt.make_set_cursor(cursor_y, 1))
            self.becho_rendered(jrline)
            cursor_y += 1
            if cursor_y >= self.term_height:
                break

    def bufecho_header(self):
        sversion = self._format_version()
        fversion = pt.Fragment(sversion, _Styles.HEADER_VERSION)

        self._bufecho_actions("Modes", self.ctx.action_group_states, self.MODES_ROWNUM, fversion)

    def bufecho_footer(self):
        self._bufecho_actions("Actions", self.ctx.action_group_actions, self.ACTIONS_ROWNUM)

    def _bufecho_actions(self, help_hint: str, group: AutoGroup, rownum: int, *extras: pt.Fragment):
        result = CompositeCompressor()

        is_first: bool = True
        for idx, action in enumerate(group):
            if not action.visibility_fn(self.ctx):
                continue
            if not is_first:
                result += DisposableComposite(" ")
            is_first = False
            result.extend(action.format_hint(self.ctx))

        # if self.ctx.help_enabled:
        #     result += self._format_help_hint(help_hint)

        extras_len = sum(map(len, extras))
        free_space = self.term_width - len(result) - extras_len
        result += AdaptiveFragment(0, free_space * " ")
        result.extend(extras)
        result.compress(self.term_width)

        self.becho(self._get_status_line_fill(False, rownum))
        self.becho_rendered(result + pt.SeqIndex.RESET.assemble())

    def bufecho_filter(self):
        fill, flabel, fvalue, frightb, strlen = self._render_filter_label()
        self.becho(fill)

        total = len(self.ctx.proc_shown) + self.ctx.proc_filtered
        shown_num = len(self.ctx.proc_shown)
        obsolete = self.ctx.proc_obsolete.is_set()

        shown_st = _Styles.HEADER_NUM
        if obsolete:
            shown_st = _Styles.HEADER_NUM_OBSOLETE
        elif 0 < shown_num < self.ctx.PROMPT_TOO_MANY_PROCESSES:
            shown_st = _Styles.HEADER_NUM_ACTIVE
        elif shown_num >= self.ctx.PROMPT_TOO_MANY_PROCESSES:
            shown_st = _Styles.HEADER_NUM_CAUTION

        shown_str = f"{len(self.ctx.proc_shown):d}"
        total_str = f"{total:d}"
        if obsolete:
            shown_str = total_str = "--"

        num = (
            pt.Fragment(pt.pad(4), _Styles.HEADER)
            + pt.Fragment(shown_str, shown_st)
            + pt.Fragment("/", _Styles.HEADER_LABEL)
            + pt.Fragment(total_str, _Styles.HEADER_NUM)
            + pt.Fragment(" matches", _Styles.HEADER_LABEL)
            + pt.Fragment(pt.pad(4), _Styles.HEADER)
        )
        if self.ctx.state.name == "journal":
            ljr = pt.Fragment(f"{len(self.ctx.journal)} records total", _Styles.HEADER_LABEL)
        else:
            ljr = self.ctx.journal.last_msg()
            if isinstance(ljr, JournalRecord):
                ljr = pt.Fragment(
                    ljr.compose_brief() + ljr.dt().strftime(" (%H:%M)"), ljr.header_style
                )
            else:
                ljr = pt.Fragment(ljr, _Styles.HEADER_LABEL)

        gap = pt.Fragment((self.term_width - strlen - len(num) - len(ljr)) * " ", _Styles.HEADER)
        header = flabel + fvalue + frightb + num + gap + ljr + pt.SeqIndex.RESET.assemble()
        self.becho_rendered(header)

    def bufecho_help(self):
        self._goto(self.STATUS_ROWNUM + 1)
        self.becho_rendered("Modes", AutoLoopStyles.TEXT_SUBTITLE, nl=True)
        for state in self.ctx.action_group_states:
            self.becho_rendered(self._format_help_action(state), nl=False)

        self.becho(nl=True)
        self.becho_rendered("Actions", AutoLoopStyles.TEXT_SUBTITLE, nl=True)
        for action in self.ctx.action_group_actions:
            self.becho_rendered(self._format_help_action(action), nl=False)

    def _format_help_action(self, state: AutoAction):
        result = CompositeCompressor(
            AdaptiveFragment(1, f" {state.keys[0]}  "),
            pt.Text(state.name(self.ctx), width=10),
        )
        desc = self.ctx.help[state.name(self.ctx)]
        if self.term_width - (llen := len(result)) > 15:
            result += pt.wrap_sgr(desc, self.term_width - 2, llen, llen).strip()
        else:
            result.compress(self.term_width)
            result += "\n" + pt.wrap_sgr(desc, self.term_width - 2, 2, 2).rstrip()
        return result + "\n"

    def _render_filter_label(self) -> Iterable[pt.RT | int]:
        prompt_str = " = /"
        prompt2_str = "/"
        strlen = len(prompt_str)
        yield self._get_header_line_fill(_Styles.HEADER, self.FILTER_ROWNUM)
        yield pt.Fragment(prompt_str, _Styles.HEADER_FILTER_CHAR)

        # help_label = pt.Fragment("")
        # if self.ctx.help_enabled:
        #     help_label = self._format_help_hint(
        #         name="Filter", label=False, overwrite=_Styles.HEADER
        #     )
        # strlen += len(help_label)

        yield pt.Fragment(self.ctx.filter, _Styles.HEADER_FILTER)
        yield pt.Fragment(prompt2_str, _Styles.HEADER_FILTER_CHAR)
        # yield help_label
        strlen += len(self.ctx.filter + prompt2_str)
        yield strlen

    def _highlight_match(
        self, p: ProcessInfo, field: str, max_len: int, match: re.Match | None, generic_st: pt.Style
    ) -> pt.RT:
        st = generic_st
        if not match or not p.running or p.pending_signal:
            return pt.Fragment(pt.fit(field, max_len), st)

        parts = [_, m, _] = [*field.partition(match.group())]
        result = pt.Text()
        while len(result) < max_len and len(parts):
            part = parts.pop(0)
            st = generic_st
            if part is m:
                st = pt.Style(generic_st, fg=_DYNAMIC_FG)
            result += pt.Fragment(pt.cut(part, max_len - len(result)), st)
        if len(result) < max_len:
            result += pt.Fragment((max_len - len(result)) * " ", st)
        return result

    def _goto(self, line: int, column: int = 1):
        self.becho(pt.make_set_cursor(line, column))

    def _get_header_line_fill(
        self, st: pt.Style = _Styles.HEADER, line: int = 1, column: int = 1
    ) -> str:
        return super()._get_header_line_fill(st, line, column)

    def _format_version(self) -> str:
        if self.term_width < 45:
            return ""
        if self.term_width < 70:
            return " v" + APP_VERSION
        return f" es7s/autoterm [v{APP_VERSION}]"

    # def _format_help_hint(
    #     self,
    #     name: str,
    #     arrow: str = "←",
    #     label: bool = False,
    #     overwrite: pt.Style = pt.NOOP_STYLE,
    # ) -> pt.RT:
    #     arrow_st = pt.Style(_Styles.HELP_HINT_ICON).merge_overwrite(overwrite)
    #     name_st = pt.Style(AutotermStyles.HELP_HINT_NAME)
    #     gap = ""
    #     if label:
    #         name_st = pt.Style(_Styles.HELP_HINT_LABEL)
    #         gap = " "
    #     name_st.merge_overwrite(overwrite)
    #
    #     return DisposableComposite(
    #         pt.Fragment(f" {arrow} ", arrow_st), pt.Fragment(f"{gap}{name} ", name_st)
    #     )


class DisposableComposite(pt.Composite):
    pass
    # def render(self, *args) -> str:
    #    return super().render(*args).replace(' ', '_')


class AdaptiveFragment(pt.Fragment):
    COLLAPSE_CHAR = " "
    COLLAPSE_MAX_LVL = 4
    COLLAPSE_FNS = {
        1: lambda s: s.removeprefix,
        2: lambda s: s.removesuffix,
        3: lambda s: s.lstrip,
        4: lambda s: s.rstrip,
    }

    def __init__(self, min_len: int, string: str = "", fmt: FT = None):
        super().__init__(string, fmt)
        self._min_len = min_len
        self._collapse_lvl = 0

    def collapse(self, lvl: int = 0):
        self._collapse_lvl = lvl
        self._string = self.collapsed(lvl)

    def collapsed(self, lvl: int = 0) -> str:
        collapse_fn = self.COLLAPSE_FNS.get(lvl, lambda s: s.strip)
        return collapse_fn(self._string)(self.COLLAPSE_CHAR)

    def delta_collapse(self, lvl: int = 0) -> int:
        return len(self._string) - len(self.collapsed(lvl))

    @property
    def collapse_lvl(self) -> int:
        return self._collapse_lvl

    def shrink(self):
        self._string = self.shrinked()

    def shrinked(self) -> str:
        return self._string[: self._min_len]

    def delta_shrink(self):
        return len(self._string) - len(self.shrinked())


_AF = AdaptiveFragment
_DC = DisposableComposite


class CompositeCompressor(pt.Composite):
    def __init__(self, *parts: pt.RT):
        super().__init__(*parts)

    def append(self, part: pt.RT):
        self._parts.append(part)

    def extend(self, parts: t.Iterable[pt.RT]):
        self._parts.extend(parts)

    def compress(self, max_len: int):
        """
        5 levels of elements compression, from almost transparent to monstrously barbaric:

        * purge       delete special blank "disposable" pseudo-fragments that act as a ballast;
        * collapse    remove whitespace characters marked as removable in adaptive fragments;
        * shrink      decrease the length of adaptive fragments to minimum recommended values,
                      where the labels can still be comprehended (usually 3-4 letters);
        * chop        ignore minimum recommended value, forcefully cut out last characters of
                      the fragments that can be modified externally; try to distribute the
                      resections evenly between all fragments to make them distinguishable from
                      each other as long as possible;
        * eviscerate  throw away the rightmost fragments entirely, which is the only remaining
                      method if the external modification is not supported by element interfaces;
                      this allows to keep at least some parts of some of fragments.
        """
        if max_len == 0:
            self._parts.clear()
            return
        req_delta = len(self) - max_len
        if req_delta <= 0:
            return
        if len(self._parts[0]) > max_len:
            self._parts = deque[pt.IRenderable]([self._parts.popleft()])

        disposables = []
        adaptives = []
        fragments = []

        for part in self._parts:
            if isinstance(part, _DC):
                disposables.append(part)
            elif isinstance(part, _AF):
                adaptives.append(part)
                fragments.append(part)
            elif isinstance(part, pt.Fragment):
                fragments.append(part)

        cur_pack_lvl = 1

        while (req_delta := len(self) - max_len) > 0:
            if max_purge := sum(map(len, disposables)):
                self._purge(disposables, req_delta, max_purge)
                self._debug_compress_level("I")
                disposables.clear()
                continue

            if cur_pack_lvl < _AF.COLLAPSE_MAX_LVL and sum(
                map(lambda af: af.delta_collapse(cur_pack_lvl), adaptives)
            ):
                self._collapse(adaptives, cur_pack_lvl)
                self._debug_compress_level(f"II ({cur_pack_lvl})")
                cur_pack_lvl += 1
                continue

            if max_shrink := sum(map(_AF.delta_shrink, adaptives)):
                self._shrink(adaptives, req_delta - max_shrink)
                self._debug_compress_level("III")
                adaptives.clear()
                continue

            if max_chop := sum(map(len, fragments)):
                self._chop(fragments, req_delta, max_chop)
                self._debug_compress_level("IV")
                fragments.clear()
                continue

            self._eviscerate(max_len)
            self._debug_compress_level("V")
            break  # от греха

    def _debug_compress_level(self, level: str):
        get_logger().trace(f"Level {level} compression applied: length {len(self)}")

    def _purge(self, disposables: list[_DC], req_delta: int, max_purge: int):
        if req_delta - max_purge > 0:
            for d in disposables:
                self._parts.remove(d)
            return
        for d in sorted(disposables, key=lambda d: -len(d)):
            if req_delta <= 0:
                break
            req_delta -= len(d)
            self._parts.remove(d)

    def _collapse(self, adaptives: list[_AF], lvl: int):
        [a.collapse(lvl) for a in adaptives]

    def _shrink(self, adaptives: list[_AF], req_remain: int):
        [a.shrink() for a in adaptives]

    def _chop(self, fragments: list[pt.Fragment], req_delta: int, delta_chop: int):
        if req_delta - delta_chop > 0:
            for f in fragments:
                self._parts.remove(f)
            return
        chop_ratio = req_delta / len(fragments)
        for f in fragments:
            if req_delta <= 0:
                break
            req_delta -= (chop := ceil(len(f) * chop_ratio))
            if chop >= len(f):
                self._parts.remove(f)
            else:
                f._string = f._string[:-chop]

    def _eviscerate(self, max_len: int):
        while len(self) > max_len and len(self._parts):
            self._parts.pop()
