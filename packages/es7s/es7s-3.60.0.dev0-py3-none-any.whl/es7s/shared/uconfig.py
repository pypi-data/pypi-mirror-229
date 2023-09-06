# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2021-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
from __future__ import annotations

import os
import typing as t
from collections import deque
from configparser import ConfigParser as BaseConfigParser
from contextlib import contextmanager
from dataclasses import dataclass
from importlib import resources
from os import makedirs, path
from os.path import dirname, isfile
import pytermor as pt
from .log import get_logger, format_attrs, format_path
from .path import RESOURCE_PACKAGE, get_user_data_dir, get_user_config_dir
from .. import APP_NAME

_merged_uconfig: UserConfig | None = None
_default_uconfig: UserConfig | None = None


@dataclass
class UserConfigParams:
    default: bool = False


class UserConfig(BaseConfigParser):
    _init_hooks: t.ClassVar[deque[t.Callable[[], None]]] = deque()

    @classmethod
    def add_init_hook(cls, fn: t.Callable[[], None]) -> None:
        cls._init_hooks.append(fn)

    @classmethod
    def trigger_init_hooks(cls):
        while len(cls._init_hooks):
            cls._init_hooks.popleft()()

    def __init__(self, params: UserConfigParams = None):
        self.params = params or UserConfigParams()
        super().__init__(interpolation=None)

        self._invalid: RuntimeError | None = None
        self._already_logged_options: t.Set[t.Tuple[str, str]] = set()
        self._logging_enabled = True

    # def read(self, *args) -> list[str]:
    #     if not (read_ok := super().read(*args)):
    #         return read_ok
    #     self._sectproxy = SectionProxy(self._sections)
    #     return read_ok

    def get(self, section: str, option: str, *args, **kwargs) -> t.Any:
        self.ensure_validity()
        log_msg = f"Getting config value: {section}.{option}"
        result = None
        try:
            result = super().get(section, option, *args, **kwargs)
        except Exception:
            raise
        finally:
            if self._logging_enabled:
                log_msg += f" = " + (
                    '"' + result.replace("\n", " ") + '"' if result else str(result)
                )
                get_logger().debug(log_msg)
        return result

    def getintlist(self, section: str, option: str, *_, **__) -> list[int]:
        try:
            return [*map(int, filter(None, self.get(section, option).splitlines()))]
        except ValueError as e:
            raise RuntimeError(f"Conversion to [int] failed for: {section}.{option}") from e

    def get_subsections(self, section: str) -> list[str]:
        return [*filter(lambda s: s.startswith(section + "."), self.sections())]

    def get_monitor_debug_mode(self) -> bool:
        if (env_var := os.getenv("ES7S_MONITOR_DEBUG", None)) is not None:
            return bool(env_var != "")
        if (req_with_verb := get_logger().setup.display_monitor_debugging_markup) is not None:
            return req_with_verb
        if (config_var := self.getboolean("monitor", "debug", fallback=None)) is not None:
            return config_var
        return False

    def get_indicator_debug_mode(self) -> bool:
        if (env_var := os.getenv("ES7S_INDICATOR_DEBUG", None)) is not None:
            return True if env_var != "" else False
        return self.getboolean("indicator", "debug", fallback=False)

    def get_cli_debug_io_mode(self) -> bool:
        if (env_var := os.getenv("ES7S_CLI_DEBUG_IO", None)) is not None:
            return True if env_var != "" else False
        with self._disabled_logging():
            return self.getboolean("cli", "debug-io", fallback=False)

    def invalidate(self):
        self._invalid = True

    def ensure_validity(self):
        if self._invalid:
            raise RuntimeError(
                "Config can be outdated. Do not cache config instances (at most "
                "-- store as local variables in the scope of the single function), "
                "call get_config() to get the fresh one instead."
            )

    def set(self, section: str, option: str, value: str | None = ...) -> None:
        raise RuntimeError(
            "Do not call set() directly, use rewrite_user_value(). "
            "Setting config values directly can lead to writing default "
            "values into user's config even if they weren't there at "
            "the first place."
        )

    def _set(self, section: str, option: str, value: str | None = ...) -> None:
        self.ensure_validity()
        if self._logging_enabled:
            log_msg = f'Setting config value: {section}.{option} = "{value}"'
            get_logger().info(log_msg)

        super().set(section, option, value)

    @contextmanager
    def _disabled_logging(self, **_):
        self._logging_enabled = False
        try:
            yield
        finally:
            self._logging_enabled = True


def get_default_filepath() -> str:
    filename = "es7s.conf.d"
    user_path = os.path.join(get_user_data_dir(), filename)
    get_logger(require=False).debug(f"User config path:   {format_path(user_path)}")

    if os.path.isfile(user_path):
        if os.path.islink(user_path):
            return os.readlink(user_path)
        return user_path
    else:
        dc_filepath = str(resources.path(RESOURCE_PACKAGE, "es7s.conf.d"))
        if not os.environ.get("ES7S_TESTS", None):
            get_logger(require=False).warning(
                f"Dist(=default) config not found in user data dir, "
                f"loading from app data dir instead: {format_path(dc_filepath)}"
            )
        return dc_filepath


def get_local_filepath() -> str:
    local_dir = get_user_config_dir()
    local_path = path.join(local_dir, f"{APP_NAME}.conf")

    get_logger(require=False).debug(f"Local config path:  {format_path(local_path)}")
    return local_path


def get_merged(require=True) -> UserConfig | None:
    if not _merged_uconfig:
        if require:
            raise pt.exception.NotInitializedError(UserConfig)
        return None
    return _merged_uconfig


def get_dist() -> UserConfig | None:
    return _default_uconfig


def init(params: UserConfigParams = None):
    for k, v in os.environ.items():
        if k.startswith('ES7S'):
            get_logger().debug(f'Environ: {k:30s}={format_attrs(v)}')

    global _default_uconfig, _merged_uconfig
    default_filepath = get_default_filepath()
    local_filepath = get_local_filepath()

    if _default_uconfig:
        _default_uconfig.invalidate()
    _default_uconfig = _make(default_filepath)

    if not isfile(local_filepath):
        reset(False)

    filepaths = [default_filepath]
    if params and not params.default:
        filepaths += [local_filepath]

    if _merged_uconfig:
        _merged_uconfig.invalidate()
    _merged_uconfig = _make(*filepaths, params=params)

    get_logger().info("Configs initialized")
    UserConfig.trigger_init_hooks()


def _make(*filepaths: str, params: UserConfigParams = None) -> UserConfig:
    uconfig = UserConfig(params)
    read_ok = uconfig.read(filepaths)
    get_logger().info("Merging config from " + format_attrs(map(format_path, filepaths)))

    if len(read_ok) != len(filepaths):
        read_failed = set(filepaths) - set(read_ok)
        get_logger().warning("Failed to read config(s): " + ", ".join(read_failed))
    if len(read_ok) == 0:
        raise RuntimeError(f"Failed to initialize config")
    return uconfig


def reset(backup: bool = True) -> str | None:
    """Return path to backup file, if any."""
    user_config_filepath = get_local_filepath()
    makedirs(dirname(user_config_filepath), exist_ok=True)
    get_logger().debug(f'Making default config in: "{user_config_filepath}"')

    user_backup_filepath = None
    if backup and os.path.exists(user_config_filepath):
        user_backup_filepath = user_config_filepath + ".bak"
        os.rename(user_config_filepath, user_backup_filepath)
        get_logger().info(f'Original file renamed to: "{user_backup_filepath}"')

    header = True
    with open(user_config_filepath, "wt") as user_cfg:
        with open(get_default_filepath(), "rt") as default_cfg:
            for idx, line in enumerate(default_cfg.readlines()):
                if header and line.startswith(("#", ";", "\n")):
                    continue  # remove default config header comments
                header = False

                if line.startswith(("#", "\n")):  # remove section separators
                    continue  # and empty lines
                elif line.startswith("["):  # keep section definitions, and
                    if user_cfg.tell():  # prepend the first one with a newline
                        line = "\n" + line
                elif line.startswith("syntax-version"):  # keep syntax-version
                    pass
                elif line.startswith(";"):  # keep examples, triple-comment out to distinguish
                    line = "###" + line.removeprefix(";")
                else:  # keep default values as commented out examples
                    line = "# " + line

                user_cfg.write(line)
                get_logger().trace(line.strip(), f"{idx+1}| ")

    return user_backup_filepath


def rewrite_value(section: str, option: str, value: str | None) -> None:
    local_filepath = get_local_filepath()
    source_uconfig = _make(local_filepath)

    if not source_uconfig.has_section(section):
        source_uconfig.add_section(section)
    source_uconfig._set(section, option, value)  # noqa

    get_logger().debug(f'Writing config to: "{local_filepath}"')
    with open(local_filepath, "wt") as user_cfg:
        source_uconfig.write(user_cfg)

    init(_merged_uconfig.params)


#
# class SectionProxy:
#     def upd(self, _k, _v):
#         if _k in self._attrs:
#             compose = [self._attrs.get(_k), _v]
#             self._attrs.update({_k: compose})
#             setattr(self, _k, compose)
#             return
#         self._attrs.update({_k: _v})
#         setattr(self, _k, _v)
#
#     def __init__(self, items):
#         self._attrs = dict()
#         for k, v in items.items():
#             k = k.replace('-', '_')
#             if isinstance(v, dict):
#                 if '.' in k:
#                     k, subk = k.split('.', 1)
#                     if not (prox := getattr(self, k, None)):
#                         self.upd(k, prox := SectionProxy({}))
#                     prox.upd(subk, SectionProxy(v))
#                     continue
#                 self.upd(k, SectionProxy(v))
#                 continue
#             self.upd(k, v)
#
#     lvl = 0
#     def __repr__(self):
#         SectionProxy.lvl += 1
#         def iter():
#             if isinstance(self, SectionProxy):
#                 i = self._attrs
#             elif isinstance(self, dict):
#                 i = self
#             elif isinstance(self, list):
#                 i = {idx: val for idx, val in enumerate(self)}
#             else:
#                 yield repr(self)
#                 return
#             for k, v in i.items():
#                 yield ("  "*SectionProxy.lvl) + str(k) +  (':\n' if  isinstance(v,( SectionProxy, dict, list)) else ' = ')  +  SectionProxy.__repr__(v)
#         result = '\n'.join(iter())
#         SectionProxy.lvl -= 1
#         return result
