"""Builds the drawcustom element list for one printer's status page.

The returned list is passed unmodified as the ``payload`` field of the
``open_epaper_link.drawcustom`` service call — see
https://github.com/OpenEPaperLink/Home_Assistant_Integration/blob/main/docs/drawcustom/supported_types.md
for the element vocabulary.
"""

from __future__ import annotations

from typing import Any

from .bambu import PrintSnapshot, format_clock, format_duration_minutes, format_temp


def render_not_found(width: int, height: int) -> list[dict[str, Any]]:
    """Placeholder page for when the configured printer has no data yet."""
    return [
        {
            "type": "text",
            "value": "No Bambu Lab printer data",
            "x": width // 2,
            "y": height // 2 - 10,
            "size": max(12, height // 10),
            "anchor": "mm",
            "color": "black",
            "max_width": width - 8,
        },
        {
            "type": "text",
            "value": "Check the Bambu Lab integration",
            "x": width // 2,
            "y": height // 2 + 14,
            "size": max(10, height // 14),
            "anchor": "mm",
            "color": "black",
            "max_width": width - 8,
        },
    ]


def render_snapshot(
    snap: PrintSnapshot, width: int, height: int, colors: list[str]
) -> list[dict[str, Any]]:
    accent = "red" if "red" in colors else "black"
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
        ("Nozzle", format_temp(snap.nozzle_temp, snap.target_nozzle_temp)),
        ("Bed", format_temp(snap.bed_temp, snap.target_bed_temp)),
    ]
    if snap.chamber_temp is not None:
        temps.append(("Chamber", format_temp(snap.chamber_temp, snap.target_chamber_temp)))

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
        ("Start", format_clock(snap.start_state)),
        ("Remaining", format_duration_minutes(snap.remaining_minutes)),
        ("End", format_clock(snap.end_state)),
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
