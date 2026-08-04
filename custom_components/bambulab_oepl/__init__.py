"""Bambu Lab OEPL Display: pushes live print status to an e-ink tag.

Reads printer state from the ha-bambulab integration
(https://github.com/greghesp/ha-bambulab) and pushes a rendered status page
to an OpenEPaperLink tag (https://github.com/OpenEPaperLink/Home_Assistant_Integration)
on a user-configurable interval, via the ``open_epaper_link.drawcustom``
service. Both integrations are hard prerequisites; this one never talks to a
printer or a tag's radio directly.
"""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval

from .bambu import build_snapshot, has_printer_entities
from .const import (
    CONF_COLORS,
    CONF_HEIGHT,
    CONF_PRINTER_NAME,
    CONF_PRINTER_SERIAL,
    CONF_REFRESH_MINUTES,
    CONF_TAG_DEVICE_ID,
    CONF_WIDTH,
    DEFAULT_COLORS,
    DEFAULT_HEIGHT,
    DEFAULT_REFRESH_MINUTES,
    DEFAULT_WIDTH,
    MAX_REFRESH_MINUTES,
    MIN_REFRESH_MINUTES,
    OEPL_DOMAIN,
    OEPL_SERVICE_DRAWCUSTOM,
)
from .render import render_not_found, render_snapshot

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = []


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    refresh_minutes = entry.options.get(CONF_REFRESH_MINUTES, DEFAULT_REFRESH_MINUTES)
    refresh_minutes = max(MIN_REFRESH_MINUTES, min(MAX_REFRESH_MINUTES, refresh_minutes))

    async def _async_update(_now=None) -> None:
        try:
            await _async_push_update(hass, entry, refresh_minutes)
        except Exception as err:  # noqa: BLE001 - keep the interval loop alive
            _LOGGER.warning("Failed to update display for %s: %s", entry.title, err)

    entry.async_on_unload(
        async_track_time_interval(hass, _async_update, timedelta(minutes=refresh_minutes))
    )
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))

    # Push once immediately so the tag doesn't sit blank until the first
    # interval tick.
    hass.async_create_task(_async_update())

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return True


async def _async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def _async_push_update(hass: HomeAssistant, entry: ConfigEntry, refresh_minutes: int) -> None:
    options = entry.options
    serial = options.get(CONF_PRINTER_SERIAL)
    tag_device_id = options.get(CONF_TAG_DEVICE_ID)
    if not serial or not tag_device_id:
        _LOGGER.warning("%s: config entry is missing printer/tag options", entry.title)
        return

    printer_name = options.get(CONF_PRINTER_NAME, serial)
    width = options.get(CONF_WIDTH, DEFAULT_WIDTH)
    height = options.get(CONF_HEIGHT, DEFAULT_HEIGHT)
    colors = options.get(CONF_COLORS, DEFAULT_COLORS)

    if has_printer_entities(hass, serial):
        snapshot = build_snapshot(hass, serial, printer_name)
        elements = render_snapshot(snapshot, width, height, colors)
    else:
        elements = render_not_found(width, height)

    # Wake the tag up right when the next update is due, not on OEPL's
    # generic default — keeps battery-powered tags from checking in more
    # often than we actually have anything new to show them.
    ttl_seconds = max(30, min(86400, refresh_minutes * 60))

    await hass.services.async_call(
        OEPL_DOMAIN,
        OEPL_SERVICE_DRAWCUSTOM,
        {
            "device_id": [tag_device_id],
            "payload": elements,
            "background": "white",
            "rotate": 0,
            "dither": "0",
            "ttl": ttl_seconds,
        },
        blocking=True,
    )
