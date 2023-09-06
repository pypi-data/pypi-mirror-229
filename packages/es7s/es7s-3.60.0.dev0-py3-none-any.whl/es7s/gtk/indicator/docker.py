# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

from es7s.shared import SocketMessage, DockerInfo
from ._base import _BaseIndicator


class IndicatorDocker(_BaseIndicator[DockerInfo]):
    def __init__(self):
        self.config_section = "indicator.docker"

        super().__init__(
            indicator_name="docker",
            socket_topic="docker",
            icon_name_default="warning",
            title="Docker",
            pseudo_hide=True,
        )

    def _render(self, msg: SocketMessage[DockerInfo]):
        running = msg.data.get("running")
        restarting = msg.data.get("restarting")

        self._hidden.value = restarting.match_amount == 0
        self._update_details(
            "\n".join(
                [
                    f"{running.match_amount} running",
                    f"{restarting.match_amount} restarting"
                    + (":" if restarting.match_amount else ""),
                ]
            )
            + "\n · ".join(["", *restarting.container_names])
        )
        self._update_visibility()
