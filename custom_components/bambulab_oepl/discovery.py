"""Device-registry discovery for Bambu Lab printers and OpenEPaperLink tags.

Both live in the public, documented device registry — not either
integration's own internal runtime objects — matching the approach used by
https://github.com/N30Z/HA-OEPL-Framework for the same kind of lookup.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import (
    BAMBU_DOMAIN,
    DEFAULT_COLORS,
    DEFAULT_HEIGHT,
    DEFAULT_WIDTH,
    OEPL_AP_IDENTIFIER,
    OEPL_DOMAIN,
)
from .tag_types import guess_colors, guess_dimensions

_HW_VERSION_RE = re.compile(r"^\s*(\d+)\s*x\s*(\d+)\s*$", re.IGNORECASE)


@dataclass(frozen=True)
class PrinterInfo:
    """A Bambu Lab printer device found in the HA device registry."""

    device_id: str
    serial: str
    name: str


@dataclass(frozen=True)
class TagInfo:
    """An OpenEPaperLink tag device found in the HA device registry."""

    device_id: str
    mac: str
    name: str
    model: str | None
    hw_version: str | None


def _identifier_value(identifiers: set[tuple[str, ...]], domain: str) -> str | None:
    for identifier in identifiers:
        # Identifiers are conventionally (domain, id) 2-tuples, but this scans
        # every device in the registry (not just the ones we care about), so
        # index defensively instead of destructuring.
        if len(identifier) < 2 or identifier[0] != domain:
            continue
        return identifier[1]
    return None


def discover_bambu_printers(hass: HomeAssistant) -> list[PrinterInfo]:
    """Find every Bambu Lab printer device (``bambu_lab`` integration)."""
    device_registry = dr.async_get(hass)
    printers: list[PrinterInfo] = []
    for device in device_registry.devices.values():
        serial = _identifier_value(device.identifiers, BAMBU_DOMAIN)
        if serial is None:
            continue
        name = device.name_by_user or device.name or serial
        printers.append(PrinterInfo(device_id=device.id, serial=serial, name=name))
    return printers


def discover_oepl_tags(hass: HomeAssistant) -> list[TagInfo]:
    """Find every OpenEPaperLink tag device, excluding the AP/hub itself."""
    device_registry = dr.async_get(hass)
    tags: list[TagInfo] = []
    for device in device_registry.devices.values():
        mac = _identifier_value(device.identifiers, OEPL_DOMAIN)
        if mac is None or mac == OEPL_AP_IDENTIFIER:
            continue
        name = device.name_by_user or device.name or mac
        tags.append(
            TagInfo(
                device_id=device.id,
                mac=mac,
                name=name,
                model=device.model,
                hw_version=device.hw_version,
            )
        )
    return tags


def guess_tag_capabilities(tag: TagInfo) -> tuple[int, int, list[str]]:
    """Best-effort (width, height, colors) guess for a discovered tag.

    Width/height come straight from the device registry's ``hw_version``
    (OpenEPaperLink sets this to ``"<width>x<height>"`` from the exact same
    hardware table it uses to size the image it generates) when available —
    that's more trustworthy than name matching, since a few hardware types
    share a display name across different resolutions. Colors have no
    registry equivalent, so those are always guessed from the model name.
    """
    width: int | None = None
    height: int | None = None
    if tag.hw_version:
        match = _HW_VERSION_RE.match(tag.hw_version)
        if match:
            width, height = int(match.group(1)), int(match.group(2))

    if width is None or height is None:
        dims = guess_dimensions(tag.model)
        if dims is not None:
            width, height = dims

    colors = guess_colors(tag.model)

    return (
        width if width is not None else DEFAULT_WIDTH,
        height if height is not None else DEFAULT_HEIGHT,
        colors if colors is not None else list(DEFAULT_COLORS),
    )
