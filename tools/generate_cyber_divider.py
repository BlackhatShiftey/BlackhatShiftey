#!/usr/bin/env python3
"""Render the Canticle spectral cube relay for GitHub profile dividers."""

from __future__ import annotations

from collections import Counter
from datetime import date
import hashlib
import json
import math
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable

import PIL
from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
PREVIEW = ROOT / "preview"
GIF_OUT = ASSETS / "cyber-divider.gif"
PNG_OUT = ASSETS / "cyber-divider.png"
META_OUT = ASSETS / "cyber-divider.provenance.json"
CONTACT_SHEET_OUT = PREVIEW / "cyber-divider-motion-sheet.png"

WIDTH = 1000
HEIGHT = 72
LINE_Y = 36
FRAME_COUNT = 48
FRAME_RATE = 12
LOOP_DURATION_SECONDS = FRAME_COUNT / FRAME_RATE
CAMERA_DISTANCE = 8.0
CUBE_X = (415, 449, 483, 517, 551, 585)
CUBE_COLORS = (
    "#ff6090",
    "#e478d0",
    "#c4a7e7",
    "#7dcfff",
    "#73daca",
    "#e0af68",
)
PALETTE = (
    "#f7768e",
    "#ff9e64",
    "#e0af68",
    "#9ece6a",
    "#7dcfff",
    "#7aa2f7",
    "#e478d0",
)
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

Vertex = tuple[float, float, float]
Face = tuple[Vertex, Vertex, Vertex, Vertex]

FACES: tuple[tuple[Vertex, Face], ...] = (
    ((1.0, 0.0, 0.0), ((1, -1, -1), (1, 1, -1), (1, 1, 1), (1, -1, 1))),
    ((-1.0, 0.0, 0.0), ((-1, -1, 1), (-1, 1, 1), (-1, 1, -1), (-1, -1, -1))),
    ((0.0, 1.0, 0.0), ((-1, 1, -1), (-1, 1, 1), (1, 1, 1), (1, 1, -1))),
    ((0.0, -1.0, 0.0), ((-1, -1, 1), (-1, -1, -1), (1, -1, -1), (1, -1, 1))),
    ((0.0, 0.0, 1.0), ((-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1))),
    ((0.0, 0.0, -1.0), ((1, -1, -1), (-1, -1, -1), (-1, 1, -1), (1, 1, -1))),
)


def rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))


def mix(first: tuple[int, int, int], second: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    return tuple(round(first[index] + (second[index] - first[index]) * amount) for index in range(3))


def spectrum(amount: float) -> tuple[int, int, int]:
    colors = [rgb(color) for color in PALETTE]
    scaled = (amount % 1.0) * len(colors)
    index = int(scaled)
    return mix(colors[index], colors[(index + 1) % len(colors)], scaled - index)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def smoothstep(value: float) -> float:
    value = clamp(value)
    return value * value * (3.0 - 2.0 * value)


def normalize(vector: Vertex) -> Vertex:
    length = math.sqrt(sum(component * component for component in vector))
    return tuple(component / length for component in vector)


def rotate(vertex: Vertex, ax: float, ay: float, az: float) -> Vertex:
    x, y, z = vertex
    cos_x, sin_x = math.cos(ax), math.sin(ax)
    y, z = y * cos_x - z * sin_x, y * sin_x + z * cos_x
    cos_y, sin_y = math.cos(ay), math.sin(ay)
    x, z = x * cos_y + z * sin_y, -x * sin_y + z * cos_y
    cos_z, sin_z = math.cos(az), math.sin(az)
    return x * cos_z - y * sin_z, x * sin_z + y * cos_z, z


def project(vertex: Vertex, center_x: float, center_y: float, scale: float) -> tuple[float, float]:
    x, y, z = vertex
    perspective = CAMERA_DISTANCE / (CAMERA_DISTANCE - z)
    return center_x + x * scale * perspective, center_y - y * scale * perspective


def shade(color: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    return tuple(round(clamp(channel * amount, 0, 255)) for channel in color)


def draw_signal_line(image: Image.Image) -> None:
    """Draw a quiet carrier so the cube glows own the RGB motion."""
    carrier = Image.new("RGBA", image.size, (0, 0, 0, 0))
    carrier_draw = ImageDraw.Draw(carrier)
    carrier_draw.line((22, LINE_Y, 978, LINE_Y), fill=(59, 61, 87, 205), width=1)
    carrier_draw.line((36, LINE_Y, 964, LINE_Y), fill=(86, 95, 137, 54), width=2)
    image.alpha_composite(carrier.filter(ImageFilter.GaussianBlur(1.6)))
    image.alpha_composite(carrier)
    draw = ImageDraw.Draw(image)
    draw.line((22, 29, 22, 43), fill=(86, 95, 137, 230), width=1)
    draw.line((22, LINE_Y, 36, LINE_Y), fill=(86, 95, 137, 230), width=1)
    draw.line((978, 29, 978, 43), fill=(86, 95, 137, 230), width=1)
    draw.line((964, LINE_Y, 978, LINE_Y), fill=(86, 95, 137, 230), width=1)


def relay_state(phase: float, index: int) -> tuple[float, float]:
    start = index * 0.085
    local = (phase - start) % 1.0
    active_window = 0.40
    if local >= active_window:
        return 0.0, 0.0
    progress = local / active_window
    return math.sin(math.pi * progress) ** 2, smoothstep(progress)


def draw_cube(image: Image.Image, index: int, phase: float) -> None:
    bump, progress = relay_state(phase, index)
    direction = -1.0 if index % 2 else 1.0
    base_ax = 0.48 + index * 0.025
    base_ay = -0.62 + index * 0.035
    base_az = (-0.11 if index % 2 else 0.09)
    ax = base_ax + direction * math.tau * progress
    ay = base_ay + math.tau * progress
    az = base_az + direction * 0.32 * math.sin(math.tau * progress)
    scale = 6.6 + 5.4 * bump
    center_x = CUBE_X[index]
    center_y = LINE_Y - 4.6 * math.sin(math.pi * progress) * bump
    base_color = rgb(CUBE_COLORS[index])

    outer_glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    outer_draw = ImageDraw.Draw(outer_glow)
    outer_radius_x = round(scale * (1.85 + 0.45 * bump))
    outer_radius_y = round(scale * (1.55 + 0.35 * bump))
    outer_draw.ellipse(
        (
            center_x - outer_radius_x,
            center_y - outer_radius_y,
            center_x + outer_radius_x,
            center_y + outer_radius_y,
        ),
        fill=(*base_color, round(58 + 142 * bump)),
    )
    image.alpha_composite(outer_glow.filter(ImageFilter.GaussianBlur(7.0)))

    inner_glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    inner_draw = ImageDraw.Draw(inner_glow)
    inner_radius_x = round(scale * (1.25 + 0.25 * bump))
    inner_radius_y = round(scale * (1.05 + 0.20 * bump))
    inner_draw.ellipse(
        (
            center_x - inner_radius_x,
            center_y - inner_radius_y,
            center_x + inner_radius_x,
            center_y + inner_radius_y,
        ),
        fill=(*base_color, round(98 + 132 * bump)),
    )
    image.alpha_composite(inner_glow.filter(ImageFilter.GaussianBlur(2.6)))

    light = normalize((-0.45, 0.85, 0.65))
    visible_faces: list[tuple[float, list[tuple[float, float]], tuple[int, int, int], tuple[int, int, int]]] = []
    for normal, face in FACES:
        rotated_normal = rotate(normal, ax, ay, az)
        if rotated_normal[2] <= 0.02:
            continue
        rotated_face = [rotate(vertex, ax, ay, az) for vertex in face]
        projected = [project(vertex, center_x, center_y, scale) for vertex in rotated_face]
        depth = sum(vertex[2] for vertex in rotated_face) / len(rotated_face)
        light_amount = sum(rotated_normal[axis] * light[axis] for axis in range(3))
        face_amount = clamp(0.48 + 0.48 * max(0.0, light_amount) + 0.12 * rotated_normal[2], 0.38, 1.08)
        fill = shade(base_color, face_amount)
        outline = mix(base_color, (255, 255, 255), 0.42 + 0.20 * bump)
        visible_faces.append((depth, projected, fill, outline))

    visible_faces.sort(key=lambda item: item[0])
    draw = ImageDraw.Draw(image)
    for _, polygon, fill, outline in visible_faces:
        draw.polygon(polygon, fill=(*fill, 255))
        draw.line((*polygon, polygon[0]), fill=(*outline, 245), width=1, joint="curve")

    highlight_radius = max(1, round(1.0 + bump))
    highlight_x = center_x - scale * 0.28
    highlight_y = center_y - scale * 0.40
    draw.ellipse(
        (
            highlight_x - highlight_radius,
            highlight_y - highlight_radius,
            highlight_x + highlight_radius,
            highlight_y + highlight_radius,
        ),
        fill=(255, 255, 255, round(105 + 110 * bump)),
    )


def draw_frame(frame_index: int) -> Image.Image:
    phase = frame_index / FRAME_COUNT
    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw_signal_line(image)
    for index in range(len(CUBE_X)):
        draw_cube(image, index, phase)

    draw = ImageDraw.Draw(image)
    draw.ellipse((395, LINE_Y - 1.5, 398, LINE_Y + 1.5), fill=(255, 96, 144, 230))
    draw.ellipse((602, LINE_Y - 1.5, 605, LINE_Y + 1.5), fill=(115, 218, 202, 230))
    return image


def ffmpeg_version() -> str:
    result = subprocess.run(["ffmpeg", "-version"], check=True, capture_output=True, text=True)
    return result.stdout.splitlines()[0]


def encode_gif(frames: Iterable[Image.Image]) -> None:
    with tempfile.TemporaryDirectory(prefix="canticle-divider-") as temporary:
        frame_dir = Path(temporary)
        for index, frame in enumerate(frames):
            frame.save(frame_dir / f"frame-{index:03d}.png", optimize=True)
        subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-framerate",
                str(FRAME_RATE),
                "-i",
                str(frame_dir / "frame-%03d.png"),
                "-filter_complex",
                "[0:v]split[a][b];"
                "[a]palettegen=max_colors=192:reserve_transparent=1:transparency_color=000000:stats_mode=diff[p];"
                "[b][p]paletteuse=dither=bayer:bayer_scale=3:alpha_threshold=32:diff_mode=rectangle",
                "-loop",
                "0",
                str(GIF_OUT),
            ],
            check=True,
        )


def render_contact_sheet(frames: list[Image.Image]) -> None:
    PREVIEW.mkdir(exist_ok=True)
    sheet = Image.new("RGB", (1000, 252), rgb("#0d1117"))
    draw = ImageDraw.Draw(sheet)
    label_font = ImageFont.truetype(FONT_MONO, 12)
    indexes = (0, 8, 16, 24, 32, 40)
    for cell, frame_index in enumerate(indexes):
        column = cell % 2
        row = cell // 2
        x = column * 500
        y = row * 84
        preview = frames[frame_index]
        preview = preview.resize((480, 35), Image.Resampling.LANCZOS)
        cell_background = Image.new("RGBA", preview.size, (*rgb("#0d1117"), 255))
        cell_background.alpha_composite(preview)
        sheet.paste(cell_background.convert("RGB"), (x + 10, y + 24))
        draw.text((x + 12, y + 5), f"FRAME {frame_index:02d}  /  {frame_index / FRAME_RATE:0.2f}s", font=label_font, fill=rgb("#7dcfff"))
    sheet.save(CONTACT_SHEET_OUT, optimize=True)


def validate_outputs() -> None:
    with Image.open(GIF_OUT) as gif:
        if gif.size != (WIDTH, HEIGHT):
            raise RuntimeError(f"unexpected GIF size: {gif.size}")
        if getattr(gif, "n_frames", 1) != FRAME_COUNT:
            raise RuntimeError(f"unexpected GIF frame count: {getattr(gif, 'n_frames', 1)}")
    with Image.open(PNG_OUT) as poster:
        if poster.size != (WIDTH, HEIGHT):
            raise RuntimeError(f"unexpected PNG size: {poster.size}")


def encoded_gif_durations() -> list[int]:
    durations: list[int] = []
    with Image.open(GIF_OUT) as gif:
        for frame_index in range(gif.n_frames):
            gif.seek(frame_index)
            durations.append(int(gif.info.get("duration", 0)))
    return durations


def main() -> int:
    ASSETS.mkdir(exist_ok=True)
    frames = [draw_frame(index) for index in range(FRAME_COUNT)]
    encode_gif(frames)
    frames[18].save(PNG_OUT, optimize=True)
    render_contact_sheet(frames)
    validate_outputs()
    durations = encoded_gif_durations()
    duration_counts = Counter(durations)

    metadata = {
        "asset": GIF_OUT.name,
        "approval_state": "approved_for_profile",
        "brand": "Canticle Research",
        "composer": "tools/generate_cyber_divider.py",
        "generated_date": date.today().isoformat(),
        "dimensions": [WIDTH, HEIGHT],
        "frame_count": FRAME_COUNT,
        "frame_rate": FRAME_RATE,
        "nominal_frame_duration_ms": round(1000 / FRAME_RATE, 3),
        "encoded_frame_duration_counts_ms": {str(value): count for value, count in sorted(duration_counts.items())},
        "encoded_total_duration_ms": sum(durations),
        "loop_duration_seconds": LOOP_DURATION_SECONDS,
        "motion": "staggered relay; each cube grows, bobs, intensifies its own color glow, and completes a smooth off-axis X/Y tumble before settling",
        "carrier_line_motion": "none; static neutral terminal carrier",
        "individual_cube_glow": True,
        "renderer": f"Pillow {PIL.__version__} projected 3D geometry",
        "encoder": ffmpeg_version(),
        "transparent_background": True,
        "palette": list(PALETTE),
        "cube_colors": list(CUBE_COLORS),
        "static_poster": PNG_OUT.name,
        "static_poster_frame": 18,
        "static_poster_sha256": sha256(PNG_OUT),
        "gif_sha256": sha256(GIF_OUT),
    }
    META_OUT.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    print(f"rendered {GIF_OUT.relative_to(ROOT)} ({WIDTH}x{HEIGHT}, {FRAME_COUNT} frames, {LOOP_DURATION_SECONDS:.1f}s)")
    print(f"rendered {PNG_OUT.relative_to(ROOT)} (reduced-motion poster)")
    print(f"rendered {CONTACT_SHEET_OUT.relative_to(ROOT)}")
    print(f"gif bytes: {GIF_OUT.stat().st_size}")
    print(f"gif sha256: {metadata['gif_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
