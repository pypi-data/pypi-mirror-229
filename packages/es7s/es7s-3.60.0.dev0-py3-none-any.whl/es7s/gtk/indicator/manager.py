# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import datetime
import os
import pickle
import re
import signal
import sys
import typing
from dataclasses import dataclass

import pytermor as pt

from es7s import APP_VERSION
from es7s.shared import SocketMessage, get_merged_uconfig
from es7s.shared import IClientIPC, NullClient
from ._base import IIndicator, CheckMenuItemConfig, _BaseIndicator, _BoolState, _StaticState


@dataclass
class _ExternalBoolState(_BoolState):
    ext: IIndicator = None

    def click(self):
        phs = self.ext.public_hidden_state
        if phs.is_set():
            phs.clear()
            self._update_config(True)
        else:
            phs.set()
            self._update_config(False)


class IndicatorManager(_BaseIndicator):
    _ICON_NAME_DEFAULT = "es7s-v2.png"
    _ICON_NAME_ACTIVITY = "es7s-v2-ai.png"

    _ACTIVITY_INDICATOR_INTERVAL_TICKS = 30

    def __init__(self, indicators: list[IIndicator]):
        self.config_section = "indicator.manager"
        self._indicators = indicators

        self._label_sys_time_state = _BoolState(
            config_var=(self.config_section, "label-system-time"),
            gconfig=CheckMenuItemConfig("Show system time", sep_before=True),
        )
        self._label_self_uptime_state = _BoolState(
            config_var=(self.config_section, "label-self-uptime"),
            gconfig=CheckMenuItemConfig("Show self uptime"),
        )
        self._label_tick_nums = _BoolState(
            config_var=(self.config_section, "label-tick-nums"),
            gconfig=CheckMenuItemConfig("Show tick nums"),
        )
        self._icon_demo_state = _BoolState(
            config_var=("indicator", "icon-demo"),
            gconfig=CheckMenuItemConfig("Icon demo mode", sep_before=True),
        )
        self._debug_state = _BoolState(
            config_var=("indicator", "debug"), gconfig=CheckMenuItemConfig("Debug mode")
        )
        self._restart_state = _StaticState(
            callback=self._restart, gconfig=CheckMenuItemConfig("Restart (shutdown)")
        )

        self._restart_timeout_min = get_merged_uconfig().getint(
            self.config_section, "restart-timeout-min"
        )

        super().__init__(
            indicator_name="manager",
            icon_name_default=self._ICON_NAME_DEFAULT,
            title=f"es7s/core {APP_VERSION}",
            details=False,
            states=[
                self._restart_state,
                self._label_sys_time_state,
                self._label_self_uptime_state,
                self._label_tick_nums,
                self._icon_demo_state,
                self._debug_state,
            ],
        )
        self._get_scc_current(rotate=False).monitor_data_buf.append(
            pickle.dumps(
                SocketMessage(data=None, timestamp=2147483647),
                protocol=pickle.HIGHEST_PROTOCOL,
            )
        )
        self._render_result("", icon=self._icon_name_default)

    def _make_socket_client(self, socket_topic: str, indicator_name: str) -> IClientIPC:
        return NullClient()

    def _restart(self, *_):
        self._update_mtimes()
        # should be run as a service and thus
        # expected to be restarted by systemd,
        # so simply perform a suicide:
        os.kill(os.getpid(), signal.SIGINT)

    def _update_mtimes(self):
        # update the modification time of
        # directory tree up to two levels
        # for GNOME to ignore cached code
        # and reload the fresh one instead
        # (doesnt work though)
        entrypoint_path = sys.argv[0]
        if os.path.islink(entrypoint_path):
            entrypoint_path = os.readlink(entrypoint_path)
        if not os.path.exists(entrypoint_path):
            return

        os.utime(entrypoint_path)
        parent_dir = os.path.dirname(entrypoint_path)

        for _ in range(2):
            parent_dir = os.path.abspath(os.path.join(parent_dir, ".."))
            if not os.path.isdir(parent_dir):
                continue
            os.utime(parent_dir)

    def _init_state(self, states: list = None):
        def transform_title(i: IIndicator) -> str:
            title = re.sub(r"(?i)[^\w/]+", " ", i.title).strip()
            if i._pseudo_hide:
                return f"{title} (~)"
            return title

        super()._init_state(states)
        for idx, indic in enumerate(self._get_togglable_indicators()):
            sep_before = (idx == 0)
            cfg = CheckMenuItemConfig(transform_title(indic), sep_before=sep_before)
            state = _ExternalBoolState(
                config_var=(indic.config_section, "display"),
                ext=indic,
            )
            self._state_map.put(cfg, state)

    def _get_togglable_indicators(self) -> typing.Iterable[IIndicator]:
        def iter():
            for idx, indic in enumerate(reversed(self._indicators)):
                if not indic._auto_visibility:
                    yield idx, indic

        def sorter(v: tuple[int, IIndicator]) -> int:
            return v[0] + 1000 * int(v[1]._pseudo_hide)

        yield from (v[1] for v in sorted(iter(), key=sorter))

    def _on_before_update(self):
        if self._state.abs_running_time_sec // 60 >= self._restart_timeout_min:
            self._restart()

    def _render(self, msg: SocketMessage[None]):
        result = []
        if self._label_sys_time_state:
            result.append(datetime.datetime.now().strftime("%H:%M:%S"))
        if self._label_self_uptime_state:
            result.append(pt.format_time_ms(self._state.abs_running_time_sec * 1e3))
        if self._label_tick_nums:
            if int(self._state.abs_running_time_sec) % 14 >= 7:
                result.append(f"R {self._state.tick_render_num}")
            else:
                result.append(f"U {self._state.tick_update_num}")

        icon = (self._ICON_NAME_DEFAULT, self._ICON_NAME_ACTIVITY)[self._state.tick_update_num % self._ACTIVITY_INDICATOR_INTERVAL_TICKS == 1]
        self._render_result("".join(f"[{s}]" for s in result), icon=icon)
