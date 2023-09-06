# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
from es7s.cli._base_opts_params import CMDTYPE_BUILTIN, CMDTRAIT_X11
from es7s.cli._decorators import cli_command, cli_argument, cli_option, catch_and_log_and_exit
from es7s.shared import run_subprocess, run_detached
from es7s.shared.path import XDOTOOL_PATH


@cli_command(
    __file__,
    type=CMDTYPE_BUILTIN,
    traits=[CMDTRAIT_X11],
    short_help="read directives list from es7s configs and invoke xdotool",
)
@cli_argument(
    "preset",
    type=str,
    required=True,
)
@catch_and_log_and_exit
class invoker:
    def __init__(self, preset: str, **kwargs):
        self.run(preset)

    def run(self):
        run_detached([
            XDOTOOL_PATH,
        ])
