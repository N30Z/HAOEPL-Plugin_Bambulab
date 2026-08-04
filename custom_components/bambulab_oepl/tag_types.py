"""Bundled OpenEPaperLink hardware capability table.

Generated from the tag hardware definitions shipped in
https://github.com/OpenEPaperLink/OpenEPaperLink/tree/master/resources/tagtypes
(the same source the OpenEPaperLink integration itself uses to size a tag's
display buffer). Keyed by a normalized version of the tag's HA device `model`
string, which OpenEPaperLink sets to that same hardware type's display name.

Used only to guess a tag's *colors* (red/yellow support) at config-flow time;
width/height are read directly off the device's `hw_version` attribute instead
(more authoritative — see discovery.py), since a handful of hardware types share
an identical display name with different resolutions.
"""

from __future__ import annotations

# key -> (display_name, width, height, colors)
TAG_TYPES: dict[str, tuple[str, int, int, list[str]]] = {
    'acep 4.01': ('ACeP 4.01', 640, 400, ['black', 'red', 'white', 'yellow']),
    'ble epd bwr 2.9" silabs': ('BLE EPD BWR 2.9" Silabs', 384, 168, ['black', 'red', 'white']),
    'ble tft 128x128': ('BLE TFT 128x128', 128, 128, ['black', 'red', 'white']),
    'bwry example': ('BWRY example', 360, 184, ['black', 'red', 'white', 'yellow']),
    'chroma 7.4"': ('Chroma 7.4"', 640, 384, ['black', 'red', 'white']),
    'chroma aeon 74 7.4"': ('Chroma Aeon 74 7.4"', 800, 480, ['black', 'red', 'white']),
    'chroma29 2.9"': ('Chroma29 2.9"', 296, 128, ['black', 'red', 'white']),
    'chroma42 4.2"': ('Chroma42 4.2"', 400, 300, ['black', 'red', 'white']),
    'gdem1085z51 10.85"': ('GDEM1085Z51 10.85"', 1360, 480, ['black', 'red', 'white']),
    'gicisky ble epd bw 2.13"': ('Gicisky BLE EPD BW 2.13"', 250, 128, ['black', 'white']),
    'gicisky ble epd bw 2.9"': ('Gicisky BLE EPD BW 2.9"', 296, 128, ['black', 'white']),
    'gicisky ble epd bwr 2.13"': ('Gicisky BLE EPD BWR 2.13"', 250, 128, ['black', 'red', 'white']),
    'gicisky ble epd bwr 2.9"': ('Gicisky BLE EPD BWR 2.9"', 296, 128, ['black', 'red', 'white']),
    'gicisky ble epd bwr 4.2"': ('Gicisky BLE EPD BWR 4.2"', 400, 300, ['black', 'red', 'white']),
    'gicisky ble tft 2.13"': ('Gicisky BLE TFT 2.13"', 250, 136, ['black', 'white']),
    'hd150 5.83" bwr': ('HD150 5.83" BWR', 648, 480, ['black', 'red', 'white']),
    'hs 2.00" bwy': ('HS 2.00" BWY', 152, 200, ['black', 'white', 'yellow']),
    'hs 2.13" bwr high res': ('HS 2.13" BWR High Res', 296, 144, ['black', 'red', 'white']),
    'hs 2.9" highres': ('HS 2.9" HighRes', 384, 168, ['black', 'red', 'white']),
    'hs bw 2.13"': ('HS BW 2.13"', 256, 128, ['black', 'white']),
    'hs bw 2.13" lowres': ('HS BW 2.13" LowRes', 212, 104, ['black', 'white']),
    'hs bw 3.5"': ('HS BW 3.5"', 384, 184, ['black', 'white']),
    'hs bwr 2.13"': ('HS BWR 2.13"', 256, 128, ['black', 'red', 'white']),
    'hs bwr 2.66"': ('HS BWR 2.66"', 296, 152, ['black', 'red', 'white']),
    'hs bwr 3.5"': ('HS BWR 3.5"', 384, 184, ['black', 'red', 'white']),
    'hs bwr 5,83"': ('HS BWR 5,83"', 648, 480, ['black', 'red', 'white']),
    'hs bwry 2,00"': ('HS BWRY 2,00"', 152, 200, ['black', 'red', 'white', 'yellow']),
    'hs bwry 2,60"': ('HS BWRY 2,60"', 296, 152, ['black', 'red', 'white', 'yellow']),
    'hs bwry 2,9"': ('HS BWRY 2,9"', 296, 128, ['black', 'red', 'white', 'yellow']),
    'hs bwry 3,5"': ('HS BWRY 3,5"', 384, 184, ['black', 'red', 'white', 'yellow']),
    'hs bwry 7,5"': ('HS BWRY 7,5"', 800, 480, ['black', 'red', 'white', 'yellow']),
    'hs bwy 3.46"': ('HS BWY 3.46"', 480, 176, ['black', 'white', 'yellow']),
    'hs bwy 3.5"': ('HS BWY 3.5"', 384, 184, ['black', 'white', 'yellow']),
    'hs bwy 7,5"': ('HS BWY 7,5"', 800, 480, ['black', 'white', 'yellow']),
    'lilygo tpanel 4"': ('LILYGO TPANEL 4"', 480, 480, ['black', 'red', 'white']),
    'm2 1.54"': ('M2 1.54"', 152, 152, ['black', 'red', 'white']),
    'm2 2.2"': ('M2 2.2"', 212, 104, ['black', 'red', 'white']),
    'm2 2.6"': ('M2 2.6"', 296, 152, ['black', 'red', 'white']),
    'm2 2.7"': ('M2 2.7"', 264, 176, ['black', 'red', 'white']),
    'm2 2.9"': ('M2 2.9"', 296, 128, ['black', 'red', 'white']),
    'm2 2.9" (uc8151)': ('M2 2.9" (UC8151)', 296, 128, ['black', 'red', 'white']),
    'm2 4.2"': ('M2 4.2"', 400, 300, ['black', 'red', 'white']),
    'm2 4.2" uc': ('M2 4.2" UC', 400, 300, ['black', 'red', 'white']),
    'm2 7.4"': ('M2 7.4"', 640, 384, ['black', 'red', 'white']),
    'm2 7.5" bw': ('M2 7.5" BW', 640, 384, ['black', 'white']),
    'm3 1.3" peghook': ('M3 1.3" Peghook', 144, 200, ['black', 'red', 'white']),
    'm3 1.6"': ('M3 1.6"', 200, 200, ['black', 'red', 'white']),
    'm3 1.6" 200px bwry': ('M3 1.6" 200px BWRY', 200, 200, ['black', 'red', 'white', 'yellow']),
    'm3 1.6" bwry': ('M3 1.6" BWRY', 168, 168, ['black', 'red', 'white', 'yellow']),
    'm3 11.6"': ('M3 11.6"', 960, 640, ['black', 'red', 'white']),
    'm3 11.6" bwry': ('M3 11.6" BWRY', 960, 640, ['black', 'red', 'white', 'yellow']),
    'm3 12.2"': ('M3 12.2"', 960, 768, ['black', 'red', 'white']),
    'm3 2.2 lite"': ('M3 2.2 Lite"', 250, 128, ['black', 'red', 'white']),
    'm3 2.2"': ('M3 2.2"', 296, 160, ['black', 'red', 'white']),
    'm3 2.2" bw': ('M3 2.2" BW', 296, 160, ['black', 'white']),
    'm3 2.2" bwry': ('M3 2.2" BWRY', 296, 160, ['black', 'red', 'white', 'yellow']),
    'm3 2.4" bwry': ('M3 2.4" BWRY', 296, 168, ['black', 'red', 'white', 'yellow']),
    'm3 2.6"': ('M3 2.6"', 360, 184, ['black', 'red', 'white']),
    'm3 2.6" bw': ('M3 2.6" BW', 360, 184, ['black', 'white']),
    'm3 2.6" bwry': ('M3 2.6" BWRY', 360, 184, ['black', 'red', 'white', 'yellow']),
    'm3 2.7"': ('M3 2.7"', 300, 200, ['black', 'red', 'white']),
    'm3 2.9"': ('M3 2.9"', 384, 168, ['black', 'red', 'white']),
    'm3 2.9" bw': ('M3 2.9" BW', 384, 168, ['black', 'white']),
    'm3 2.9" bwry': ('M3 2.9" BWRY', 384, 168, ['black', 'red', 'white', 'yellow']),
    'm3 3.0" bwry': ('M3 3.0" BWRY', 400, 168, ['black', 'red', 'white', 'yellow']),
    'm3 3.5" bwry rtl': ('M3 3.5" BWRY RTL', 480, 224, ['black', 'red', 'white', 'yellow']),
    'm3 4.2"': ('M3 4.2"', 400, 300, ['black', 'red', 'white']),
    'm3 4.2" bwry': ('M3 4.2" BWRY', 400, 300, ['black', 'red', 'white', 'yellow']),
    'm3 4.2" bwy': ('M3 4.2" BWY', 400, 300, ['black', 'white', 'yellow']),
    'm3 4.3"': ('M3 4.3"', 522, 152, ['black', 'red', 'white']),
    'm3 4.3" bwry': ('M3 4.3" BWRY', 522, 152, ['black', 'red', 'white', 'yellow']),
    'm3 5.81" bw': ('M3 5.81" BW', 720, 256, ['black', 'white']),
    'm3 5.81" bwr': ('M3 5.81" BWR', 720, 256, ['black', 'red', 'white']),
    'm3 5.81" v2 bwr': ('M3 5.81" V2 BWR', 720, 256, ['black', 'red', 'white']),
    'm3 5.85"': ('M3 5.85"', 792, 272, ['black', 'red', 'white']),
    'm3 5.85" bw': ('M3 5.85" BW', 792, 272, ['black', 'white']),
    'm3 6.0"': ('M3 6.0"', 600, 448, ['black', 'red', 'white']),
    'm3 7.5"': ('M3 7.5"', 800, 480, ['black', 'red', 'white']),
    'm3 7.5" bwry': ('M3 7.5" BWRY', 800, 480, ['black', 'red', 'white', 'yellow']),
    'm3 8.2" bwry': ('M3 8.2" BWRY', 1024, 576, ['black', 'red', 'white', 'yellow']),
    'm3 9.7"': ('M3 9.7"', 960, 672, ['black', 'red', 'white']),
    'opticon 2.2"': ('Opticon 2.2"', 250, 128, ['black', 'red', 'white', 'yellow']),
    'opticon 2.9"': ('Opticon 2.9"', 296, 128, ['black', 'red', 'white', 'yellow']),
    'opticon 4.2"': ('Opticon 4.2"', 400, 300, ['black', 'red', 'white']),
    'opticon 7.5"': ('Opticon 7.5"', 640, 384, ['black', 'red', 'white']),
    'spectra 7.3': ('Spectra 7.3', 800, 480, ['black', 'red', 'white', 'yellow']),
    'st-gm29mt1 2.9"': ('ST‐GM29MT1 2.9"', 296, 128, ['black', 'white']),
    'st-gm29xxf 2.9"': ('ST‐GM29XXF 2.9"', 296, 128, ['black', 'white']),
    'tft 160x80': ('TFT 160x80', 160, 80, ['black', 'red', 'white']),
    'tft 240x320': ('TFT 240x320', 320, 172, ['black', 'red', 'white']),
    'tft 320x172': ('TFT 320x172', 320, 172, ['black', 'red', 'white']),
    'tlsr bw 2.13"': ('TLSR BW 2.13"', 250, 136, ['black', 'white']),
    'tlsr bwr 1.54"': ('TLSR BWR 1.54"', 200, 200, ['black', 'red', 'white']),
    'tlsr bwr 2.13"': ('TLSR BWR 2.13"', 264, 136, ['black', 'red', 'white']),
    'tlsr bwr 4.2"': ('TLSR BWR 4.2"', 400, 300, ['black', 'red', 'white']),
}


def _normalize(model: str) -> str:
    return (
        model.strip()
        .lower()
        .replace("\u201c", '"').replace("\u201d", '"').replace("\u2033", '"')
        .replace("\u2010", "-").replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-")
        .replace("\u2018", "'").replace("\u2019", "'")
    )


def guess_colors(model: str | None) -> list[str] | None:
    """Best-effort colors guess for a tag model name, or None if unknown."""
    if not model:
        return None
    entry = TAG_TYPES.get(_normalize(model))
    return list(entry[3]) if entry else None


def guess_dimensions(model: str | None) -> tuple[int, int] | None:
    """Best-effort width/height guess for a tag model name.

    Only used as a fallback when a device has no usable `hw_version`; a handful
    of hardware types share a display name with different resolutions, so this
    is less trustworthy than the device registry's own `hw_version`.
    """
    if not model:
        return None
    entry = TAG_TYPES.get(_normalize(model))
    return (entry[1], entry[2]) if entry else None
