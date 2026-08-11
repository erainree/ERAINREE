"""
make_ascii_svg.py

Converts a prepped grayscale photo (source-prepped.png) into a
self-typing, monochrome ASCII-art SVG.

How it works:
  1. Downsample the image to a character grid (~100 wide).
  2. Map each cell's average brightness to a character from a
     density ramp (bright -> sparse, dark -> dense).
  3. Emit each row as SVG text, wrapped in a clip-path that wipes
     left-to-right, staggered top-to-bottom, so the portrait looks
     like it's "typing" itself in once, then freezes.

Usage:
    python3 make_ascii_svg.py
Reads:
    source-prepped.png
Writes:
    avi-ascii.svg   (feel free to rename the output in this script)
"""

from PIL import Image

# bright (sparse) -> dark (dense); leading space clears background to nothing
RAMP = " .`:-=+*cs#%@"

# Grid dimensions (character columns x rows)
GRID_WIDTH = 100
GRID_HEIGHT = 53

# Because terminal characters are taller than they are wide, we
# under-sample vertically relative to horizontal so the final image
# doesn't look squished. This factor tweaks that.
CHAR_ASPECT = 0.55

FONT_SIZE = 8
CHAR_WIDTH = FONT_SIZE * 0.6
LINE_HEIGHT = FONT_SIZE * CHAR_ASPECT * 2

FILL_COLOR = "#c9d1d9"  # light gray, monochrome
BG_COLOR = "transparent"

# Animation timing
ROW_STAGGER = 0.05   # seconds between each row starting
WIPE_DURATION = 0.6  # seconds for a single row's left-to-right wipe


def image_to_ascii_grid(image_path: str, cols: int, rows: int) -> list[str]:
    img = Image.open(image_path).convert("L")
    img = img.resize((cols, rows), Image.LANCZOS)
    pixels = list(img.getdata())

    ascii_rows = []
    ramp_len = len(RAMP) - 1
    for r in range(rows):
        row_chars = []
        for c in range(cols):
            brightness = pixels[r * cols + c]  # 0 (dark) - 255 (bright)
            # Bright pixels -> low ramp index (sparse/space),
            # dark pixels -> high ramp index (dense).
            ramp_index = int((255 - brightness) / 255 * ramp_len)
            row_chars.append(RAMP[ramp_index])
        ascii_rows.append("".join(row_chars))
    return ascii_rows


def escape_xml(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_svg(ascii_rows: list[str]) -> str:
    width = int(len(ascii_rows[0]) * CHAR_WIDTH) + 20
    height = int(len(ascii_rows) * LINE_HEIGHT) + 20

    svg_parts = []
    svg_parts.append(
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="monospace" font-size="{FONT_SIZE}">'
    )
    svg_parts.append(
        f'<style>text {{ fill: {FILL_COLOR}; white-space: pre; }}</style>'
    )

    for row_index, row in enumerate(ascii_rows):
        y = 10 + row_index * LINE_HEIGHT + FONT_SIZE
        row_width = len(row) * CHAR_WIDTH
        start_delay = row_index * ROW_STAGGER
        clip_id = f"clip{row_index}"

        # Clip path that animates from 0 width to full row width,
        # creating the left-to-right "typing" wipe for this row.
        svg_parts.append(f'<clipPath id="{clip_id}">')
        svg_parts.append(
            f'<rect x="10" y="{y - FONT_SIZE}" width="0" height="{FONT_SIZE + 4}">'
            f'<animate attributeName="width" from="0" to="{row_width}" '
            f'begin="{start_delay}s" dur="{WIPE_DURATION}s" '
            f'fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1" />'
            f'</rect>'
        )
        svg_parts.append('</clipPath>')

        svg_parts.append(
            f'<text x="10" y="{y}" clip-path="url(#{clip_id})">{escape_xml(row)}</text>'
        )

    svg_parts.append('</svg>')
    return "\n".join(svg_parts)


if __name__ == "__main__":
    ascii_rows = image_to_ascii_grid("source-prepped.png", GRID_WIDTH, GRID_HEIGHT)
    svg = build_svg(ascii_rows)

    with open("avi-ascii.svg", "w") as f:
        f.write(svg)

    print(f"Saved avi-ascii.svg ({GRID_WIDTH}x{GRID_HEIGHT} character grid)")
