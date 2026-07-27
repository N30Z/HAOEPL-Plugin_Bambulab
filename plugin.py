"""Bambu Lab printer live-progress plugin for the OEPL Page Framework.

Requires the ha-bambulab integration (https://github.com/greghesp/ha-bambulab)
to already be set up in this Home Assistant instance. This plugin only reads
the sensor entities that integration exposes for each printer device (domain
``bambu_lab``); it never talks to a printer directly.

One page is created per detected Bambu Lab printer device (``printer_<serial>``),
so multiple printers each get their own page automatically. If no printer has
been discovered yet, a single fallback ``printer`` page shows a hint instead
of crashing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.core import HomeAssistant, State
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from custom_components.oepl_framework.plugin_api import OeplPlugin, PageContext, PageDescriptor

BAMBU_DOMAIN = "bambu_lab"
FALLBACK_PAGE_ID = "printer"
PAGE_ID_PREFIX = "printer_"

# ha-bambulab registers each printer sensor's unique_id as f"{serial}_{KEY}".
KEY_NOZZLE_TEMP = "nozzle_temp"
KEY_TARGET_NOZZLE_TEMP = "target_nozzle_temp"
KEY_BED_TEMP = "bed_temp"
KEY_TARGET_BED_TEMP = "target_bed_temp"
KEY_CHAMBER_TEMP = "chamber_temp"
KEY_TARGET_CHAMBER_TEMP = "target_chamber_temp"
KEY_PRINT_PROGRESS = "print_progress"
KEY_CURRENT_LAYER = "current_layer"
KEY_TOTAL_LAYERS = "total_layers"
KEY_SUBTASK_NAME = "subtask_name"
KEY_GCODE_FILE = "gcode_file"
KEY_PRINT_STATUS = "print_status"
KEY_STAGE = "stage"
KEY_START_TIME = "start_time"
KEY_END_TIME = "end_time"
KEY_REMAINING_TIME = "remaining_time"

UNAVAILABLE_STATES = (None, "", "unknown", "unavailable")


@dataclass(frozen=True)
class BambuPrinter:
    """A Bambu Lab printer device found in the HA device registry."""

    serial: str
    name: str


@dataclass
class PrintSnapshot:
    """Everything needed to render one printer's page."""

    printer_name: str
    status: str
    nozzle_temp: float | None
    target_nozzle_temp: float | None
    bed_temp: float | None
    target_bed_temp: float | None
    chamber_temp: float | None
    target_chamber_temp: float | None
    progress: int
    current_layer: int | None
    total_layers: int | None
    job_name: str
    start_state: State | None
    end_state: State | None
    remaining_minutes: float | None


def _discover_printers(hass: HomeAssistant) -> list[BambuPrinter]:
    device_registry = dr.async_get(hass)
    printers: list[BambuPrinter] = []
    for device in device_registry.devices.values():
        for domain, serial in device.identifiers:
            if domain == BAMBU_DOMAIN:
                name = device.name_by_user or device.name or serial
                printers.append(BambuPrinter(serial=serial, name=name))
                break
    return printers


def _find_printer(hass: HomeAssistant, serial: str) -> BambuPrinter | None:
    for printer in _discover_printers(hass):
        if printer.serial == serial:
            return printer
    return None


def _get_state(hass: HomeAssistant, serial: str, key: str) -> State | None:
    entity_id = er.async_get(hass).async_get_entity_id("sensor", BAMBU_DOMAIN, f"{serial}_{key}")
    if entity_id is None:
        return None
    return hass.states.get(entity_id)


def _state_value(state: State | None) -> str | None:
    if state is None or state.state in UNAVAILABLE_STATES:
        return None
    return state.state


def _as_float(state: State | None) -> float | None:
    value = _state_value(state)
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _as_int(state: State | None) -> int | None:
    value = _as_float(state)
    return None if value is None else int(value)


def _format_temp(actual: float | None, target: float | None) -> str:
    if actual is None:
        return "n/a"
    if target and target > 0:
        return f"{actual:.0f}/{target:.0f}°C"
    return f"{actual:.0f}°C"


def _format_clock(state: State | None) -> str:
    value = _state_value(state)
    if value is None:
        return "--:--"
    parsed = dt_util.parse_datetime(value)
    if parsed is None:
        return "--:--"
    return dt_util.as_local(parsed).strftime("%H:%M")


def _format_duration_minutes(minutes: float | None) -> str:
    if minutes is None or minutes < 0:
        return "n/a"
    total_minutes = int(round(minutes))
    hours, mins = divmod(total_minutes, 60)
    if hours:
        return f"{hours}h {mins:02d}m"
    return f"{mins}m"


def _clean_job_name(name: str | None) -> str:
    if not name:
        return "No active print"
    trimmed = name.rsplit("/", 1)[-1]
    for suffix in (".gcode.3mf", ".3mf", ".gcode"):
        if trimmed.endswith(suffix):
            trimmed = trimmed[: -len(suffix)]
            break
    return trimmed or "No active print"


def _build_snapshot(hass: HomeAssistant, printer: BambuPrinter) -> PrintSnapshot:
    serial = printer.serial

    def state_for(key: str) -> State | None:
        return _get_state(hass, serial, key)

    status = (
        _state_value(state_for(KEY_STAGE))
        or _state_value(state_for(KEY_PRINT_STATUS))
        or "unknown"
    )

    job_name = _clean_job_name(
        _state_value(state_for(KEY_SUBTASK_NAME)) or _state_value(state_for(KEY_GCODE_FILE))
    )

    progress = max(0, min(100, _as_int(state_for(KEY_PRINT_PROGRESS)) or 0))

    return PrintSnapshot(
        printer_name=printer.name,
        status=status.replace("_", " ").title(),
        nozzle_temp=_as_float(state_for(KEY_NOZZLE_TEMP)),
        target_nozzle_temp=_as_float(state_for(KEY_TARGET_NOZZLE_TEMP)),
        bed_temp=_as_float(state_for(KEY_BED_TEMP)),
        target_bed_temp=_as_float(state_for(KEY_TARGET_BED_TEMP)),
        chamber_temp=_as_float(state_for(KEY_CHAMBER_TEMP)),
        target_chamber_temp=_as_float(state_for(KEY_TARGET_CHAMBER_TEMP)),
        progress=progress,
        current_layer=_as_int(state_for(KEY_CURRENT_LAYER)),
        total_layers=_as_int(state_for(KEY_TOTAL_LAYERS)),
        job_name=job_name,
        start_state=state_for(KEY_START_TIME),
        end_state=state_for(KEY_END_TIME),
        remaining_minutes=_as_float(state_for(KEY_REMAINING_TIME)),
    )


class BambulabPlugin(OeplPlugin):
    id = "bambulab"
    version = "1.0.0"

    def get_pages(self) -> list[PageDescriptor]:
        printers = _discover_printers(self.runtime.hass)
        if not printers:
            return [PageDescriptor(FALLBACK_PAGE_ID, "Bambu Lab Printer", icon="mdi:printer-3d")]
        return [
            PageDescriptor(f"{PAGE_ID_PREFIX}{printer.serial}", printer.name, icon="mdi:printer-3d")
            for printer in printers
        ]

    async def async_render_page(self, page_id: str, ctx: PageContext) -> list[dict[str, Any]]:
        width = ctx.tag_definition.display.width
        height = ctx.tag_definition.display.height
        accent = "red" if "red" in ctx.tag_definition.display.colors else "black"

        printer = self._resolve_printer(ctx.hass, page_id)
        if printer is None:
            return self._render_not_found(width, height)

        snapshot = _build_snapshot(ctx.hass, printer)
        return self._render_snapshot(snapshot, width, height, accent)

    def _resolve_printer(self, hass: HomeAssistant, page_id: str) -> BambuPrinter | None:
        if page_id == FALLBACK_PAGE_ID:
            printers = _discover_printers(hass)
            return printers[0] if printers else None
        return _find_printer(hass, page_id.removeprefix(PAGE_ID_PREFIX))

    def _render_not_found(self, width: int, height: int) -> list[dict[str, Any]]:
        return [
            {
                "type": "text",
                "value": "No Bambu Lab printer found",
                "x": width // 2,
                "y": height // 2 - 10,
                "size": max(12, height // 10),
                "anchor": "mm",
                "color": "black",
                "max_width": width - 8,
            },
            {
                "type": "text",
                "value": "Set up the Bambu Lab integration first",
                "x": width // 2,
                "y": height // 2 + 14,
                "size": max(10, height // 14),
                "anchor": "mm",
                "color": "black",
                "max_width": width - 8,
            },
        ]

    def _render_snapshot(
        self, snap: PrintSnapshot, width: int, height: int, accent: str
    ) -> list[dict[str, Any]]:
        margin = max(4, width // 40)
        elements: list[dict[str, Any]] = []

        # -- header: printer name (left) + status/stage (right) --------
        header_size = max(11, height // 11)
        name_max_width = int(width * 0.6)
        elements.append(
            {
                "type": "text",
                "value": snap.printer_name,
                "x": margin,
                "y": margin,
                "size": header_size,
                "color": "black",
                "anchor": "lt",
                "max_width": name_max_width,
                "truncate": True,
            }
        )
        elements.append(
            {
                "type": "text",
                "value": snap.status,
                "x": width - margin,
                "y": margin,
                "size": max(9, header_size - 2),
                "color": accent,
                "anchor": "rt",
                "max_width": width - name_max_width - margin * 2,
                "truncate": True,
            }
        )

        # -- dynamic 0-100% progress bar ---------------------------------
        bar_y0 = margin + header_size + 6
        bar_height = max(14, height // 8)
        elements.append(
            {
                "type": "progress_bar",
                "x_start": margin,
                "x_end": width - margin,
                "y_start": bar_y0,
                "y_end": bar_y0 + bar_height,
                "progress": snap.progress,
                "direction": "right",
                "background": "white",
                "fill": accent,
                "outline": "black",
                "width": 1,
                "show_percentage": True,
            }
        )

        # -- current / total layer ---------------------------------------
        layer_y = bar_y0 + bar_height + 6
        layer_size = max(10, height // 13)
        if snap.current_layer is not None and snap.total_layers:
            layer_text = f"Layer {snap.current_layer}/{snap.total_layers}"
        else:
            layer_text = "Layer -/-"
        elements.append(
            {
                "type": "text",
                "value": layer_text,
                "x": width // 2,
                "y": layer_y,
                "size": layer_size,
                "color": "black",
                "anchor": "mt",
            }
        )

        # -- current print job name ---------------------------------------
        name_y = layer_y + layer_size + 4
        name_size = max(10, height // 13)
        elements.append(
            {
                "type": "text",
                "value": snap.job_name,
                "x": width // 2,
                "y": name_y,
                "size": name_size,
                "color": "black",
                "anchor": "mt",
                "max_width": width - margin * 2,
                "truncate": True,
            }
        )

        # -- temperatures row (nozzle / bed / chamber) ---------------------
        temps_y = name_y + name_size + 8
        temp_label_size = max(8, height // 16)
        temp_value_size = max(10, height // 14)

        temps = [
            ("Nozzle", _format_temp(snap.nozzle_temp, snap.target_nozzle_temp)),
            ("Bed", _format_temp(snap.bed_temp, snap.target_bed_temp)),
        ]
        if snap.chamber_temp is not None:
            temps.append(("Chamber", _format_temp(snap.chamber_temp, snap.target_chamber_temp)))

        col_width = (width - margin * 2) / len(temps)
        for i, (label, value) in enumerate(temps):
            cx = int(margin + col_width * i + col_width / 2)
            elements.append(
                {
                    "type": "text",
                    "value": label,
                    "x": cx,
                    "y": temps_y,
                    "size": temp_label_size,
                    "color": "black",
                    "anchor": "mt",
                    "max_width": int(col_width) - 4,
                    "truncate": True,
                }
            )
            elements.append(
                {
                    "type": "text",
                    "value": value,
                    "x": cx,
                    "y": temps_y + temp_label_size + 2,
                    "size": temp_value_size,
                    "color": "black",
                    "anchor": "mt",
                    "max_width": int(col_width) - 4,
                    "truncate": True,
                }
            )

        # -- start / remaining / end time row -------------------------------
        times_y = temps_y + temp_label_size + 2 + temp_value_size + 10
        time_label_size = max(8, height // 17)
        time_value_size = max(9, height // 15)
        times_y = min(times_y, height - time_label_size - time_value_size - 4)

        times = [
            ("Start", _format_clock(snap.start_state)),
            ("Remaining", _format_duration_minutes(snap.remaining_minutes)),
            ("End", _format_clock(snap.end_state)),
        ]
        col_width = (width - margin * 2) / len(times)
        for i, (label, value) in enumerate(times):
            cx = int(margin + col_width * i + col_width / 2)
            elements.append(
                {
                    "type": "text",
                    "value": label,
                    "x": cx,
                    "y": times_y,
                    "size": time_label_size,
                    "color": "black",
                    "anchor": "mt",
                    "max_width": int(col_width) - 4,
                    "truncate": True,
                }
            )
            elements.append(
                {
                    "type": "text",
                    "value": value,
                    "x": cx,
                    "y": times_y + time_label_size + 2,
                    "size": time_value_size,
                    "color": "black",
                    "anchor": "mt",
                    "max_width": int(col_width) - 4,
                    "truncate": True,
                }
            )

        return elements
