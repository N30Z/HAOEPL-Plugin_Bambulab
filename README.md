# HAOEPL-Plugin_Bambulab → Bambu Lab OEPL Display

A standalone Home Assistant custom integration that pushes live Bambu Lab
print status to an [OpenEPaperLink](https://github.com/OpenEPaperLink/Home_Assistant_Integration)
e-ink tag.

> **Note:** this project used to be a plugin for
> [HA-OEPL-Framework](https://github.com/N30Z/HA-OEPL-Framework). It has
> since been rewritten as a full, self-contained Home Assistant integration
> (`custom_components/bambulab_oepl`) — the framework is no longer required.

## Prerequisites

- [ha-bambulab](https://github.com/greghesp/ha-bambulab), set up and
  connected to your printer(s). This integration only *reads* the sensor
  entities `ha-bambulab` already exposes — it never talks to a printer
  directly.
- [OpenEPaperLink](https://github.com/OpenEPaperLink/Home_Assistant_Integration),
  set up with your access point and at least one tag paired.

## What it does

Once configured, it renders a status page and pushes it to your chosen tag
via the `open_epaper_link.drawcustom` service on a repeating timer:

- Printer name and current status/stage
- A dynamic progress bar, 0–100 %
- Current layer / total layers
- Name of the current print job
- Nozzle temperature (actual/target), bed temperature (actual/target), and
  chamber temperature if the printer reports one
- Start time, remaining time, and estimated end time (local time)

If the printer has no data yet (integration still starting up, wrong
serial, etc.), the page shows a short hint instead of crashing or leaving
stale/garbled content on the tag.

## Setup

1. Copy `custom_components/bambulab_oepl` into your Home Assistant
   `config/custom_components/` folder (or install via HACS as a custom
   repository — `hacs.json` is included), then restart Home Assistant.
2. **Settings → Devices & Services → Add Integration → "Bambu Lab OEPL
   Display"**.
3. Pick the printer and the tag to show it on (skipped automatically if you
   only have one of each).
4. Confirm the display's **width/height/colors** — these are pre-filled
   automatically from the tag's detected hardware, so you normally don't
   need to touch them — and set the **refresh interval in minutes**
   (default: **1 minute**).

Every field from step 4 can be changed later from the integration's
**Configure** button, without re-adding it. Multiple printer/display pairs
are supported: just add the integration again for each pair.

## How display size is detected

Width and height are read straight from the OpenEPaperLink tag device's own
`hw_version` registry field (e.g. `"296x128"`) — the exact value OpenEPaperLink
itself computes for that tag's hardware type, so it's normally accurate
without any manual input. Extra colors (red/yellow) are guessed from the
tag's `model` name against a bundled table generated from
[OpenEPaperLink's hardware definitions](https://github.com/OpenEPaperLink/OpenEPaperLink/tree/master/resources/tagtypes);
if a model isn't recognized, colors default to black/white/red and both
width/height and colors remain freely editable in the setup/options form.

## Refresh interval & tag battery life

The configured refresh interval also sets how long the tag is told to sleep
before checking in again (the `drawcustom` service's `ttl`), so a
battery-powered tag only wakes up as often as you've actually asked for new
content — a 1-minute interval means more frequent radio wake-ups (and
faster battery drain) than, say, 15 minutes.

## Notes

- The layout is designed for landscape tags roughly 296×128 px or larger;
  it still renders on smaller/portrait displays but text truncates more
  aggressively.
- The progress bar and status text use `red` as an accent color when the
  display's configured colors include it; otherwise everything renders in
  black.
- Data freshness is bounded by both `ha-bambulab`'s own update cadence
  (local MQTT push by default) and this integration's refresh interval.
