# HAOEPL-Plugin_Bambulab

Live Bambu Lab print-progress page for the
[OEPL Page Framework](https://github.com/N30Z/HA-OEPL-Framework), showing the
current print's status on an OpenEPaperLink e-ink tag.

## Prerequisite

This plugin does **not** talk to your printer. It only reads sensor entities
that the [ha-bambulab](https://github.com/greghesp/ha-bambulab) integration
already creates in Home Assistant. Set that integration up and connect your
printer(s) first — without it, the plugin has nothing to display.

Also required: the [OEPL Page Framework](https://github.com/N30Z/HA-OEPL-Framework)
itself, and a tag paired via the
[OpenEPaperLink integration](https://github.com/OpenEPaperLink/Home_Assistant_Integration).

## What it shows

One page per detected Bambu Lab printer, auto-discovered — no manual entity
selection needed. If you have several printers, each gets its own page.

- Printer name and current status/stage (top)
- A dynamic progress bar, 0–100 %
- Current layer / total layers
- Name of the current print job
- Nozzle temperature (actual/target), bed temperature (actual/target), and
  chamber temperature if the printer reports one
- Start time, remaining time, and estimated end time (all in your Home
  Assistant instance's local time)

If no Bambu Lab printer is found yet, the page shows a short hint instead of
crashing. Missing individual values (e.g. no chamber sensor, or no active
print) show as `n/a` / `--:--` rather than breaking the layout.

## Installing

In the OEPL Page Framework's config entry, go to **Manage plugins**, then
either:

- **Discover plugins**, entering `N30Z` as the owner (repos named
  `HAOEPL-Plugin_*` are picked up automatically), or
- **Add custom plugin repository**, entering `N30Z` / `HAOEPL-Plugin_Bambulab`
  / `main` directly.

Then, under **Manage tags** for your e-ink tag, add the Bambu Lab page(s) to
its page sequence.

## Notes

- The layout is designed for landscape tags roughly 296×128 px or larger;
  it still renders on smaller/portrait displays but text truncates more
  aggressively.
- If the tag's color profile includes red, the progress bar fill and status
  text use it as an accent color; otherwise everything renders in black.
- Data is read directly from Home Assistant entity/device state — the page
  is only as fresh as `ha-bambulab`'s own update cadence (local MQTT push by
  default), plus the OEPL Page Framework's own render cycle interval for
  your tag.
