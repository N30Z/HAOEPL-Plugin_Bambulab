"""Constants for the Bambu Lab OEPL Display integration."""

from __future__ import annotations

DOMAIN = "bambulab_oepl"

# Domains of the two integrations this one depends on.
BAMBU_DOMAIN = "bambu_lab"
OEPL_DOMAIN = "open_epaper_link"

# OpenEPaperLink registers its own AP/hub device with this literal
# identifier value (as opposed to a tag's MAC) — skip it when discovering
# candidate display targets.
OEPL_AP_IDENTIFIER = "ap"

OEPL_SERVICE_DRAWCUSTOM = "drawcustom"

# -- config entry options ---------------------------------------------------

CONF_PRINTER_DEVICE_ID = "printer_device_id"
CONF_PRINTER_SERIAL = "printer_serial"
CONF_PRINTER_NAME = "printer_name"
CONF_TAG_DEVICE_ID = "tag_device_id"
CONF_TAG_NAME = "tag_name"
CONF_WIDTH = "width"
CONF_HEIGHT = "height"
CONF_COLORS = "colors"
CONF_ACCENT_COLORS = "accent_colors"
CONF_REFRESH_MINUTES = "refresh_minutes"

DEFAULT_REFRESH_MINUTES = 1
MIN_REFRESH_MINUTES = 1
MAX_REFRESH_MINUTES = 1440

DEFAULT_WIDTH = 296
DEFAULT_HEIGHT = 128
DEFAULT_COLORS: list[str] = ["black", "white", "red"]

MIN_DISPLAY_SIZE = 8
MAX_DISPLAY_SIZE = 4000
