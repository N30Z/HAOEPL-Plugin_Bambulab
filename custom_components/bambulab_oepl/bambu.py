"""Reads print-job state from the ha-bambulab integration.

Requires https://github.com/greghesp/ha-bambulab to already be set up — this
module only reads the sensor entities that integration exposes for a printer
device (domain ``bambu_lab``); it never talks to a printer directly.
"""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.core import HomeAssistant, State
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from .const import BAMBU_DOMAIN

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


@dataclass
class PrintSnapshot:
    """Everything needed to render one printer's status."""

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


# HA's canonical UnitOfTime values (homeassistant.const.UnitOfTime), plus a
# few lowercase aliases in case something reports its unit non-canonically.
_MINUTES_PER_UNIT = {
    "s": 1 / 60,
    "sec": 1 / 60,
    "second": 1 / 60,
    "seconds": 1 / 60,
    "min": 1.0,
    "mins": 1.0,
    "minute": 1.0,
    "minutes": 1.0,
    "h": 60.0,
    "hr": 60.0,
    "hrs": 60.0,
    "hour": 60.0,
    "hours": 60.0,
    "d": 60.0 * 24,
    "day": 60.0 * 24,
    "days": 60.0 * 24,
}


def _as_minutes(state: State | None) -> float | None:
    """Read a duration sensor's value in minutes, honoring its actual unit.

    ha-bambulab's ``remaining_time`` sensor has a native unit of minutes but
    a *suggested* unit of hours — Home Assistant then converts the value it
    actually exposes as ``state.state`` to hours (e.g. ``"2.283"``, not
    ``"137"``) unless the user has overridden their preferred unit in the
    entity's settings. Reading ``state.state`` as a bare number and assuming
    it's minutes silently produces a wildly wrong (far too short) remaining
    time. Converting via the state's own ``unit_of_measurement`` attribute
    is correct regardless of which unit HA (or the user) ends up showing.
    """
    value = _as_float(state)
    if value is None or state is None:
        return None
    unit = str(state.attributes.get("unit_of_measurement") or "").strip().lower()
    factor = _MINUTES_PER_UNIT.get(unit, 1.0)  # unknown/missing unit: assume native (minutes)
    return value * factor


def _clean_job_name(name: str | None) -> str:
    if not name:
        return "No active print"
    trimmed = name.rsplit("/", 1)[-1]
    for suffix in (".gcode.3mf", ".3mf", ".gcode"):
        if trimmed.endswith(suffix):
            trimmed = trimmed[: -len(suffix)]
            break
    return trimmed or "No active print"


def has_printer_entities(hass: HomeAssistant, serial: str) -> bool:
    """Whether ha-bambulab has registered any entity for this printer serial.

    Used to distinguish "no data yet" (show a hint) from a printer that's
    just idle (all its sensors exist, some just report empty/zero).
    """
    entity_registry = er.async_get(hass)
    return any(
        entity_registry.async_get_entity_id("sensor", BAMBU_DOMAIN, f"{serial}_{key}") is not None
        for key in (KEY_PRINT_STATUS, KEY_STAGE, KEY_NOZZLE_TEMP)
    )


def build_snapshot(hass: HomeAssistant, serial: str, printer_name: str) -> PrintSnapshot:
    """Read every sensor this integration needs for one printer, by serial."""

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
        printer_name=printer_name,
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
        remaining_minutes=_as_minutes(state_for(KEY_REMAINING_TIME)),
    )


def format_temp(actual: float | None, target: float | None) -> str:
    if actual is None:
        return "n/a"
    if target and target > 0:
        return f"{actual:.0f}/{target:.0f}°C"
    return f"{actual:.0f}°C"


def format_clock(state: State | None) -> str:
    value = _state_value(state)
    if value is None:
        return "--:--"
    parsed = dt_util.parse_datetime(value)
    if parsed is None:
        return "--:--"
    return dt_util.as_local(parsed).strftime("%H:%M")


def format_duration_minutes(minutes: float | None) -> str:
    if minutes is None or minutes < 0:
        return "n/a"
    total_minutes = int(round(minutes))
    hours, mins = divmod(total_minutes, 60)
    if hours:
        return f"{hours}h {mins:02d}m"
    return f"{mins}m"
