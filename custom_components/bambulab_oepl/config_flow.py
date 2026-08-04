"""Config + options flow: pick a printer, a display, and a refresh rate."""

from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_ACCENT_COLORS,
    CONF_COLORS,
    CONF_HEIGHT,
    CONF_PRINTER_DEVICE_ID,
    CONF_PRINTER_NAME,
    CONF_PRINTER_SERIAL,
    CONF_REFRESH_MINUTES,
    CONF_TAG_DEVICE_ID,
    CONF_TAG_NAME,
    CONF_WIDTH,
    DEFAULT_REFRESH_MINUTES,
    DOMAIN,
    MAX_DISPLAY_SIZE,
    MAX_REFRESH_MINUTES,
    MIN_DISPLAY_SIZE,
    MIN_REFRESH_MINUTES,
)
from .discovery import PrinterInfo, TagInfo, discover_bambu_printers, discover_oepl_tags, guess_tag_capabilities

_LOGGER = logging.getLogger(__name__)

ACCENT_COLOR_LABELS = {"red": "Red", "yellow": "Yellow"}


def _display_schema(width: int, height: int, accent_colors: list[str], refresh_minutes: int) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_WIDTH, default=width): vol.All(
                vol.Coerce(int), vol.Range(min=MIN_DISPLAY_SIZE, max=MAX_DISPLAY_SIZE)
            ),
            vol.Required(CONF_HEIGHT, default=height): vol.All(
                vol.Coerce(int), vol.Range(min=MIN_DISPLAY_SIZE, max=MAX_DISPLAY_SIZE)
            ),
            vol.Optional(CONF_ACCENT_COLORS, default=accent_colors): cv.multi_select(
                ACCENT_COLOR_LABELS
            ),
            vol.Required(CONF_REFRESH_MINUTES, default=refresh_minutes): vol.All(
                vol.Coerce(int), vol.Range(min=MIN_REFRESH_MINUTES, max=MAX_REFRESH_MINUTES)
            ),
        }
    )


class BambulabOeplConfigFlow(ConfigFlow, domain=DOMAIN):
    """Set up one printer -> one e-ink display pairing."""

    VERSION = 1

    def __init__(self) -> None:
        self._printers: list[PrinterInfo] = []
        self._tags: list[TagInfo] = []
        self._printer: PrinterInfo | None = None
        self._tag: TagInfo | None = None

    async def async_step_user(self, user_input: dict | None = None):
        self._printers = discover_bambu_printers(self.hass)
        self._tags = discover_oepl_tags(self.hass)

        if not self._printers:
            return self.async_abort(reason="no_bambu_printer")
        if not self._tags:
            return self.async_abort(reason="no_oepl_tag")

        errors: dict[str, str] = {}

        if user_input is not None:
            self._printer = next(
                (p for p in self._printers if p.device_id == user_input[CONF_PRINTER_DEVICE_ID]), None
            )
            self._tag = next(
                (t for t in self._tags if t.device_id == user_input[CONF_TAG_DEVICE_ID]), None
            )
            if self._printer is None or self._tag is None:
                errors["base"] = "selection_invalid"
            else:
                return await self._async_pick_display()
        elif len(self._printers) == 1 and len(self._tags) == 1:
            # Only one possible pairing exists yet — skip straight past the
            # picker instead of making the user confirm a foregone choice.
            self._printer = self._printers[0]
            self._tag = self._tags[0]
            return await self._async_pick_display()

        schema = vol.Schema(
            {
                vol.Required(CONF_PRINTER_DEVICE_ID): vol.In(
                    {p.device_id: p.name for p in self._printers}
                ),
                vol.Required(CONF_TAG_DEVICE_ID): vol.In(
                    {
                        t.device_id: f"{t.name} ({t.model or 'unknown model'})"
                        for t in self._tags
                    }
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def _async_pick_display(self):
        assert self._printer is not None
        assert self._tag is not None
        await self.async_set_unique_id(f"{self._printer.serial}:{self._tag.device_id}")
        self._abort_if_unique_id_configured()
        return await self.async_step_display()

    async def async_step_display(self, user_input: dict | None = None):
        assert self._printer is not None
        assert self._tag is not None
        guess_width, guess_height, guess_colors = guess_tag_capabilities(self._tag)
        guess_accents = [c for c in guess_colors if c not in ("black", "white")]

        if user_input is not None:
            colors = sorted({"black", "white", *user_input.get(CONF_ACCENT_COLORS, [])})
            options = {
                CONF_PRINTER_DEVICE_ID: self._printer.device_id,
                CONF_PRINTER_SERIAL: self._printer.serial,
                CONF_PRINTER_NAME: self._printer.name,
                CONF_TAG_DEVICE_ID: self._tag.device_id,
                CONF_TAG_NAME: self._tag.name,
                CONF_WIDTH: user_input[CONF_WIDTH],
                CONF_HEIGHT: user_input[CONF_HEIGHT],
                CONF_COLORS: colors,
                CONF_REFRESH_MINUTES: user_input[CONF_REFRESH_MINUTES],
            }
            return self.async_create_entry(
                title=f"{self._printer.name} → {self._tag.name}",
                data={},
                options=options,
            )

        return self.async_show_form(
            step_id="display",
            data_schema=_display_schema(
                guess_width, guess_height, guess_accents, DEFAULT_REFRESH_MINUTES
            ),
            description_placeholders={
                "printer": self._printer.name,
                "tag": self._tag.name,
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> BambulabOeplOptionsFlow:
        return BambulabOeplOptionsFlow()


class BambulabOeplOptionsFlow(OptionsFlow):
    """Edit the display size/colors and refresh rate after setup."""

    async def async_step_init(self, user_input: dict | None = None):
        current = self.config_entry.options

        if user_input is not None:
            colors = sorted({"black", "white", *user_input.get(CONF_ACCENT_COLORS, [])})
            new_options = dict(current)
            new_options[CONF_WIDTH] = user_input[CONF_WIDTH]
            new_options[CONF_HEIGHT] = user_input[CONF_HEIGHT]
            new_options[CONF_COLORS] = colors
            new_options[CONF_REFRESH_MINUTES] = user_input[CONF_REFRESH_MINUTES]
            return self.async_create_entry(title="", data=new_options)

        current_colors = current.get(CONF_COLORS, [])
        current_accents = [c for c in current_colors if c not in ("black", "white")]

        return self.async_show_form(
            step_id="init",
            data_schema=_display_schema(
                current.get(CONF_WIDTH, 296),
                current.get(CONF_HEIGHT, 128),
                current_accents,
                current.get(CONF_REFRESH_MINUTES, DEFAULT_REFRESH_MINUTES),
            ),
        )
