# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

import pytermor as pt

from es7s.shared import SocketMessage
from es7s.shared import (
    NetworkCountryInfo,
    NetworkLatencyInfo,
    NetworkUsageInfo,
    NetworkUsageInfoStats,
)
from ._base import CheckMenuItemConfig, WAIT_PLACEHOLDER, _BaseIndicator, _BoolState
from es7s.shared import filterf

NetworkInfo = NetworkUsageInfo | NetworkLatencyInfo | NetworkCountryInfo


class IndicatorNetwork(_BaseIndicator[NetworkInfo]):
    RENDER_INTERVAL_SEC = 1.0

    def __init__(self):
        self.config_section = "indicator.network"
        self._interface = None
        self._last_dto = dict[type, NetworkInfo]()
        self._netcom = False

        self._show_rate = _BoolState(
            config_var=(self.config_section, "label-rate"),
            gconfig=CheckMenuItemConfig("Show rate (bit/s, max)", sep_before=True),
        )
        self._show_latency = _BoolState(
            config_var=(self.config_section, "label-latency"),
            gconfig=CheckMenuItemConfig("Show latency/delivery rate"),
        )
        self._show_country = _BoolState(
            config_var=(self.config_section, "label-country"),
            gconfig=CheckMenuItemConfig("Show country code"),
        )

        self._exclude_foreign_codes = {
            *filterf(map(str.strip, self._cfg_get("exclude-foreign-codes").splitlines()))
        }

        super().__init__(
            indicator_name="network",
            socket_topic=["network-usage", "network-latency", "network-country"],
            icon_subpath="network",
            icon_name_default="disabled.svg",
            icon_path_dynamic_tpl="%s%s-%s%s.svg",
            title="Network",
            states=[self._show_rate, self._show_latency, self._show_country],
        )
        self._formatter = pt.StaticFormatter(
            pt.formatter_bytes_human,
            max_value_len=4,
            auto_color=False,
            allow_negative=False,
            allow_fractional=True,
            discrete_input=False,
            unit="",
            unit_separator="",
            pad=True,
        )

    def _update_interface(self, last_usage: NetworkUsageInfo = None):
        if not last_usage:
            return
        self._interface = last_usage.interface

    def _render(self, msg: SocketMessage[NetworkInfo]):
        last_usage = self._get_last_usage()
        if (
            last_usage
            and hasattr(msg.data, "interface")
            and self._interface != getattr(msg.data, "interface")
        ):
            self._render_no_data()
            self._last_dto.clear()
            return

        self._netcom = False
        self._last_dto.update({type(msg.data): msg.data})

        if hasattr(msg, "network_comm") and msg.network_comm:
            self._netcom = True

        if not last_usage:
            self._render_no_data()
            return

        if not last_usage.isup:
            self._render_result("N/A", "N/A", icon="down.svg")
            return

        frames, bpss = [self._get_vpn_fid_part()], []
        for uis in (last_usage.sent, last_usage.recv):
            if not uis:
                frames.append("0")
                bpss.append(None)
                continue
            frames.append(self._get_icon_frame(uis))
            bpss.append(uis.bps)
        frames.append("-nc" if self._netcom else "")

        icon = self._icon_path_dynamic_tpl % (*frames,)
        result = self._format_result(*bpss)
        self._update_details(f"[{self._interface}]\t{self._format_result(*bpss, details=True)}")
        self._render_result(result, result, icon=icon)

    def _get_vpn_fid_part(self) -> str:
        last_usage = self._get_last_usage()
        if not last_usage or not last_usage.vpn:
            return ""

        last_country = self._get_last_country_info()
        if not last_country or not last_country.country:
            return "vpnw-"

        if last_country.country.lower() in self._exclude_foreign_codes:
            return "vpn-"

        return "vpnf-"

    @property
    def _show_any(self):
        return self._show_rate or self._show_country or self._show_latency

    def _render_no_data(self):
        self._render_result("WAIT", "WAIT", icon="wait.svg")
        self._update_details(f"[{self._interface}]\t..." if self._interface else "(no interfaces)")

    def _get_last_usage(self) -> NetworkUsageInfo | None:
        if last_usage := self._last_dto.get(NetworkUsageInfo, None):
            self._update_interface(last_usage)
        return last_usage

    def _get_last_country_info(self) -> NetworkCountryInfo | None:
        return self._last_dto.get(NetworkCountryInfo, None)

    def _get_failed_ratio(self) -> float:
        if last_latency := self._last_dto.get(NetworkLatencyInfo, None):
            return last_latency.failed_ratio
        return 0.0

    def _get_icon_frame(self, uis: NetworkUsageInfoStats) -> str:
        failed_ratio = self._get_failed_ratio()
        if uis.errors or failed_ratio > 0.5:
            return "e"
        if uis.drops or failed_ratio > 0.0:
            return "w"
        if uis.bps:
            if uis.bps > 4e7:  # 40 Mbps
                return "6"
            if uis.bps > 2e7:  # 20 Mbps
                return "5"
            if uis.bps > 1e7:  # 10 Mbps
                return "4"
            if uis.bps > 1e6:  # 1 Mbps
                return "3"
            if uis.bps > 1e5:  # 100 kbps
                return "2"
            if uis.bps > 1e4:  # 10 kpbs
                return "1"
        # if uis.ratio:
        #     if uis.ratio > 0.4:
        #         return "4"
        #     if uis.ratio > 0.2:
        #         return "3"
        #     if uis.ratio > 0.1:
        #         return "2"
        #     if uis.ratio > 0.01:
        #         return "1"
        return "0"

    def _format_result(self, *bps_values: float | None, details=False) -> str:
        result = ("\t" if details else " ").join(
            filter(
                bool,
                [
                    self._format_usage(*bps_values, details=details),
                    self._format_latency(details=details),
                    self._format_country(details=details),
                ],
            )
        )
        if details:
            return result.strip()
        return result

    def _format_usage(self, *bps_values: float | None, details=False) -> str:
        if not self._show_rate and not details:
            return ""
        if details and len(bps_values) > 1:
            return f"↑{self._format_usage(bps_values[0], details=True)} ↓{self._format_usage(bps_values[1], details=True)} "
        if not any(bps_values):
            return " 0.0k"
        val = max(bps_values)
        if val < 1000:
            return "<1.0k"
        return self._formatter.format(val)

    def _format_latency(self, details=False) -> str:
        if not self._show_latency and not details:
            return ""
        if not (last_latency := self._last_dto.get(NetworkLatencyInfo, None)):
            return WAIT_PLACEHOLDER
        if last_latency.failed_ratio:
            return f"{100*(1-last_latency.failed_ratio):3.0f}%"
        val, sep, pfx, unit = pt.formatter_time_ms._format_raw(last_latency.latency_s * 1000)
        return " " * max(0, 4 - len(val + pfx + unit)) + val + pfx + unit

    def _format_country(self, details=False) -> str:
        cc = self._format_country_code(details)
        if cc and details:
            return cc + self._format_vpn(details)
        return cc

    def _format_country_code(self, details=False) -> str:
        if not self._show_country and not details:
            return ""
        if not (last_country := self._last_dto.get(NetworkCountryInfo, None)):
            return WAIT_PLACEHOLDER
        return last_country.country or ""

    def _format_vpn(self, details=False) -> str:
        if not self._show_country and not details:
            return ""
        if last_usage := self._last_dto.get(NetworkUsageInfo, None):
            return "*" if last_usage.vpn else ""
        return ""
