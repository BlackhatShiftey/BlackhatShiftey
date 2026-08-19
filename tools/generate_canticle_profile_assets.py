#!/usr/bin/env python3
"""Build the animated Canticle profile hero from approved local brand art."""

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

from PIL import __version__ as PILLOW_VERSION
from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
GHOST_SOURCE = ASSETS / "ghost-duo-square-00003.png"
GHOST_MOTION_SOURCE = ASSETS / "ghost-duo-square-00003-dance.mp4"
PNG_OUT = ASSETS / "canticle-profile-hero.png"
GIF_OUT = ASSETS / "canticle-profile-hero.gif"
CAMEO_OUT = ASSETS / "ghost-cameo.png"
META_OUT = ASSETS / "canticle-profile-hero.provenance.json"

WIDTH = 1200
HEIGHT = 440
FRAME_RATE = 12
SOURCE_FRAME_COUNT = 120
LOOP_BLEND_FRAMES = 12
FRAME_COUNT = SOURCE_FRAME_COUNT - LOOP_BLEND_FRAMES
GIF_COLORS = 96
MASCOT_SIZE = 560
MASCOT_CENTER = (960, 225)
MASCOT_POSITION = (
    round(MASCOT_CENTER[0] - MASCOT_SIZE / 2),
    round(MASCOT_CENTER[1] - MASCOT_SIZE / 2),
)
MASCOT_VISIBLE_SOURCE_BOX = (
    max(0, -MASCOT_POSITION[0]),
    max(0, -MASCOT_POSITION[1]),
    min(MASCOT_SIZE, WIDTH - MASCOT_POSITION[0]),
    min(MASCOT_SIZE, HEIGHT - MASCOT_POSITION[1]),
)
MASCOT_VISIBLE_POSITION = (
    max(0, MASCOT_POSITION[0]),
    max(0, MASCOT_POSITION[1]),
)
PALETTE = [
    "#f7768e",
    "#ff9e64",
    "#e0af68",
    "#9ece6a",
    "#7dcfff",
    "#7aa2f7",
    "#e478d0",
]

FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_MONO_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def font(size: int, *, mono: bool = False, bold: bool = False) -> ImageFont.FreeTypeFont:
    if mono:
        path = FONT_MONO_BOLD if bold else FONT_MONO
    else:
        path = FONT_SANS_BOLD if bold else FONT_SANS
    return ImageFont.truetype(path, size)


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


def gradient_background() -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), (10, 10, 16, 255))
    draw = ImageDraw.Draw(image)
    top = rgb("#0b0c12")
    middle = rgb("#1a1b26")
    bottom = rgb("#11131d")
    for y in range(HEIGHT):
        if y < HEIGHT * 0.52:
            color = mix(top, middle, y / (HEIGHT * 0.52))
        else:
            color = mix(middle, bottom, (y - HEIGHT * 0.52) / (HEIGHT * 0.48))
        draw.line((0, y, WIDTH, y), fill=(*color, 255))

    ambient = Image.new("RGBA", image.size, (0, 0, 0, 0))
    ambient_draw = ImageDraw.Draw(ambient)
    ambient_draw.ellipse((-240, -210, 430, 360), fill=(247, 118, 142, 60))
    ambient_draw.ellipse((690, -180, 1330, 460), fill=(125, 207, 255, 58))
    ambient_draw.ellipse((500, 240, 980, 650), fill=(158, 206, 106, 28))
    image.alpha_composite(ambient.filter(ImageFilter.GaussianBlur(90)))

    grid = Image.new("RGBA", image.size, (0, 0, 0, 0))
    grid_draw = ImageDraw.Draw(grid)
    for x in range(0, WIDTH, 34):
        grid_draw.line((x, 0, x, HEIGHT), fill=(125, 207, 255, 11), width=1)
    for y in range(0, HEIGHT, 34):
        grid_draw.line((0, y, WIDTH, y), fill=(125, 207, 255, 10), width=1)
    image.alpha_composite(grid)
    return image


@lru_cache(maxsize=1)
def mascot_edge_mask() -> Image.Image:
    """Return the fixed soft-edge mask used by both motion and still artwork."""
    mask = Image.new("L", (MASCOT_SIZE, MASCOT_SIZE), 255)
    pixels = mask.load()
    for y in range(MASCOT_SIZE):
        vertical = min(1.0, y / 18, (MASCOT_SIZE - 1 - y) / 30)
        for x in range(MASCOT_SIZE):
            horizontal = min(1.0, x / 145)
            pixels[x, y] = max(0, round(255 * horizontal * vertical * 0.95))
    return mask


@lru_cache(maxsize=1)
def static_mascot_source() -> Image.Image:
    """Load the approved still only when a reduced-motion frame is rendered."""
    with Image.open(GHOST_SOURCE) as source:
        return source.convert("RGB").resize(
            (MASCOT_SIZE, MASCOT_SIZE),
            Image.Resampling.LANCZOS,
        )


def decode_motion_source() -> list[Image.Image]:
    """Decode the normalized motion source without applying any camera transform."""
    result = subprocess.run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error",
            "-i", str(GHOST_MOTION_SOURCE),
            "-map", "0:v:0",
            "-frames:v", str(SOURCE_FRAME_COUNT),
            "-vf", f"scale={MASCOT_SIZE}:{MASCOT_SIZE}:flags=lanczos",
            "-pix_fmt", "rgb24",
            "-f", "rawvideo",
            "-",
        ],
        check=True,
        capture_output=True,
    )
    frame_size = MASCOT_SIZE * MASCOT_SIZE * 3
    expected_size = SOURCE_FRAME_COUNT * frame_size
    if len(result.stdout) != expected_size:
        raise RuntimeError(
            f"motion source decoded to {len(result.stdout)} bytes; expected {expected_size}"
        )
    return [
        Image.frombytes(
            "RGB",
            (MASCOT_SIZE, MASCOT_SIZE),
            result.stdout[index * frame_size : (index + 1) * frame_size],
        )
        for index in range(SOURCE_FRAME_COUNT)
    ]


def loop_motion_frame(frame_index: int, motion_frames: list[Image.Image]) -> Image.Image:
    """Return one anchored frame with a one-second end-to-start loop blend."""
    main_count = SOURCE_FRAME_COUNT - 2 * LOOP_BLEND_FRAMES
    if frame_index < main_count:
        return motion_frames[LOOP_BLEND_FRAMES + frame_index].copy()

    blend_index = frame_index - main_count
    blend_amount = (blend_index + 1) / LOOP_BLEND_FRAMES
    return Image.blend(
        motion_frames[SOURCE_FRAME_COUNT - LOOP_BLEND_FRAMES + blend_index],
        motion_frames[blend_index],
        blend_amount,
    )


def mascot_layer(source: Image.Image) -> Image.Image:
    """Place one frame at an invariant position, scale, rotation, and crop."""
    source = source.convert("RGBA")
    source.putalpha(mascot_edge_mask())
    source = source.crop(MASCOT_VISIBLE_SOURCE_BOX)
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    layer.alpha_composite(source, MASCOT_VISIBLE_POSITION)

    # The fade is phase-independent so the moving art never reduces copy contrast.
    fade = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    fade_draw = ImageDraw.Draw(fade)
    for x in range(670, 890):
        opacity = round(220 * (1 - (x - 670) / 220))
        fade_draw.line((x, 0, x, HEIGHT), fill=(10, 11, 17, opacity))
    layer.alpha_composite(fade)
    return layer


BASE = gradient_background()


def render_cameo() -> None:
    source = Image.open(GHOST_SOURCE).convert("RGB")
    source.resize((240, 240), Image.Resampling.LANCZOS).save(CAMEO_OUT, optimize=True)


def draw_gradient_text(image: Image.Image, xy: tuple[int, int], text: str, text_font: ImageFont.FreeTypeFont) -> None:
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).text(xy, text, font=text_font, fill=255)
    gradient = Image.new("RGBA", image.size, (0, 0, 0, 0))
    gradient_draw = ImageDraw.Draw(gradient)
    x_start, y_start = xy
    width = ImageDraw.Draw(mask).textbbox(xy, text, font=text_font)[2] - x_start
    for offset in range(max(1, width)):
        color = spectrum(offset / max(1, width - 1) * 0.78)
        gradient_draw.line((x_start + offset, y_start, x_start + offset, HEIGHT), fill=(*color, 255))
    gradient.putalpha(mask)
    glow = gradient.copy()
    glow.putalpha(glow.getchannel("A").point(lambda value: round(value * 0.42)))
    image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(5)))
    image.alpha_composite(gradient)


def draw_chip(draw: ImageDraw.ImageDraw, x: int, y: int, label: str, color: tuple[int, int, int]) -> int:
    chip_font = font(12, mono=True, bold=True)
    box = draw.textbbox((0, 0), label, font=chip_font)
    width = box[2] - box[0] + 28
    draw.rounded_rectangle((x, y, x + width, y + 30), radius=6, fill=(*rgb("#10131d"), 230), outline=(*color, 150), width=1)
    draw.text((x + 14, y + 8), label, font=chip_font, fill=(*color, 255))
    return x + width + 10


def draw_border(image: Image.Image) -> None:
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    step = 5
    for x in range(0, WIDTH, step):
        color = spectrum(x / WIDTH)
        draw.line((x, 1, min(WIDTH - 1, x + step), 1), fill=(*color, 225), width=3)
        draw.line((WIDTH - 1 - x, HEIGHT - 2, max(0, WIDTH - 1 - x - step), HEIGHT - 2), fill=(*color, 180), width=2)
    for y in range(0, HEIGHT, step):
        color = spectrum(0.35 + y / HEIGHT)
        draw.line((1, y, 1, min(HEIGHT - 1, y + step)), fill=(*color, 190), width=2)
        draw.line((WIDTH - 2, HEIGHT - 1 - y, WIDTH - 2, max(0, HEIGHT - 1 - y - step)), fill=(*color, 190), width=2)
    bloom = overlay.copy()
    bloom.putalpha(bloom.getchannel("A").point(lambda value: round(value * 0.38)))
    image.alpha_composite(bloom.filter(ImageFilter.GaussianBlur(6)))
    image.alpha_composite(overlay)


def draw_frame(
    frame_index: int,
    motion_frames: list[Image.Image] | None = None,
    *,
    reduced_motion: bool = False,
) -> Image.Image:
    image = BASE.copy()
    if reduced_motion:
        mascot_source = static_mascot_source()
    else:
        if motion_frames is None:
            raise ValueError("motion_frames are required for animated output")
        mascot_source = loop_motion_frame(frame_index, motion_frames)
    image.alpha_composite(mascot_layer(mascot_source))
    draw = ImageDraw.Draw(image)

    # Canticle prompt-square lockup. All identity pixels remain fixed.
    brand_color = rgb("#e0af68")
    draw.rounded_rectangle((50, 42, 112, 88), radius=10, fill=(*rgb("#090b0f"), 255), outline=(*brand_color, 255), width=2)
    draw.text((62, 50), "❯", font=font(22, mono=True, bold=True), fill=(*rgb("#9ece6a"), 255))
    draw.rectangle((91, 53, 102, 77), fill=(*brand_color, 255))
    draw.text((130, 48), "Canticle Research", font=font(23, mono=True, bold=True), fill=(*brand_color, 255))
    draw.text((131, 76), "INDEPENDENT AI RESEARCH", font=font(10, mono=True), fill=(*rgb("#7f849c"), 255), spacing=3)

    draw.text((51, 126), "OPERATOR / FOUNDER", font=font(12, mono=True, bold=True), fill=(*rgb("#9ece6a"), 255))
    draw_gradient_text(image, (47, 146), "BLACKHATSHIFTEY", font(54, bold=True))
    draw = ImageDraw.Draw(image)
    draw.text((51, 218), "AI RESEARCH  //  OPEN SOURCE  //  AGENT SYSTEMS", font=font(17, mono=True), fill=(*rgb("#c0caf5"), 255))
    draw.text((51, 252), "building inspectable systems for long-horizon intelligence", font=font(15, mono=True), fill=(*rgb("#a9b1d6"), 255))

    chip_x = 51
    chip_x = draw_chip(draw, chip_x, 292, "AI SAFETY", rgb("#f7768e"))
    chip_x = draw_chip(draw, chip_x, 292, "OPEN SOURCE AI", rgb("#7dcfff"))
    draw_chip(draw, chip_x, 292, "EMERGENCE", rgb("#9ece6a"))

    draw.line((51, 360, 724, 360), fill=(*rgb("#3b4261"), 255), width=1)
    draw.text((51, 382), "LAB / CANTICLE", font=font(11, mono=True), fill=(*rgb("#7f849c"), 255))
    draw.text((221, 382), "MODE / BUILD + VERIFY", font=font(11, mono=True), fill=(*rgb("#7f849c"), 255))
    draw.text((466, 382), "SIGNAL / PUBLIC RESEARCH", font=font(11, mono=True), fill=(*rgb("#73daca"), 255))
    draw.text((51, 409), "canticle.cc  ·  github.com/Canticle-AI-Research", font=font(11, mono=True), fill=(*rgb("#565f89"), 255))
    ghost_color = rgb("#e478d0")
    draw.rounded_rectangle((874, 388, 1162, 420), radius=7, fill=(*rgb("#0a0b0f"), 220), outline=(*ghost_color, 180), width=1)
    draw.text((892, 398), "GHOST // GIRL + SPIRIT FORMS", font=font(10, mono=True, bold=True), fill=(*ghost_color, 255))

    # Spectral accents are intentionally phase-independent; only Ghost moves.
    particles = [(760, 68, 3), (1092, 54, 4), (755, 192, 2), (1142, 220, 3), (731, 335, 4), (1082, 372, 2)]
    particle_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    particle_draw = ImageDraw.Draw(particle_layer)
    for index, (x, y, radius) in enumerate(particles):
        color = spectrum(index / len(particles))
        particle_draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*color, 180))
    image.alpha_composite(particle_layer.filter(ImageFilter.GaussianBlur(7)))
    image.alpha_composite(particle_layer)

    # The scanline texture is static; no full-width moving overlay remains.
    scanlines = Image.new("RGBA", image.size, (0, 0, 0, 0))
    scanlines_draw = ImageDraw.Draw(scanlines)
    for y in range(0, HEIGHT, 4):
        scanlines_draw.line((0, y, WIDTH, y), fill=(255, 255, 255, 7), width=1)
    image.alpha_composite(scanlines)

    draw.rounded_rectangle((6, 6, WIDTH - 7, HEIGHT - 7), radius=13, outline=(*rgb("#3b4261"), 170), width=1)
    draw_border(image)
    return image.convert("RGB")


def ffmpeg_version() -> str:
    first_line = subprocess.run(
        ["ffmpeg", "-version"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()[0]
    return first_line.removeprefix("ffmpeg version ").split(" Copyright", 1)[0]


def gif_timing(path: Path) -> tuple[list[int], int]:
    durations: list[int] = []
    with Image.open(path) as animation:
        loop_count = int(animation.info.get("loop", 0))
        for index in range(animation.n_frames):
            animation.seek(index)
            duration = animation.info.get("duration")
            if not isinstance(duration, int):
                raise RuntimeError(f"missing encoded GIF duration on frame {index}")
            durations.append(duration)
    return durations, loop_count


def main() -> int:
    if not GHOST_SOURCE.exists():
        raise SystemExit(f"missing approved brand source: {GHOST_SOURCE.relative_to(ROOT)}")
    if not GHOST_MOTION_SOURCE.exists():
        raise SystemExit(f"missing approved motion source: {GHOST_MOTION_SOURCE.relative_to(ROOT)}")

    motion_frames = decode_motion_source()
    frames = [draw_frame(index, motion_frames) for index in range(FRAME_COUNT)]
    draw_frame(0, reduced_motion=True).save(PNG_OUT, optimize=True)
    with tempfile.TemporaryDirectory(prefix="canticle-profile-") as temporary:
        frame_dir = Path(temporary)
        for index, frame in enumerate(frames):
            frame.save(frame_dir / f"frame-{index:03d}.png", optimize=True)
        subprocess.run(
            [
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-framerate", str(FRAME_RATE), "-i", str(frame_dir / "frame-%03d.png"),
                "-filter_complex",
                f"[0:v]split[a][b];[a]palettegen=max_colors={GIF_COLORS}:stats_mode=diff[p];"
                "[b][p]paletteuse=dither=none:diff_mode=rectangle",
                "-loop", "0", str(GIF_OUT),
            ],
            check=True,
        )
    render_cameo()

    encoded_durations, loop_count = gif_timing(GIF_OUT)
    duration_counts = Counter(encoded_durations)
    generated_at = datetime.now(timezone.utc)

    metadata = {
        "asset": GIF_OUT.name,
        "approval_state": "approved_for_profile",
        "brand": "Canticle Research",
        "composer": "tools/generate_canticle_profile_assets.py",
        "generated_date": generated_at.date().isoformat(),
        "generated_at_utc": generated_at.isoformat(timespec="seconds"),
        "dimensions": [WIDTH, HEIGHT],
        "frame_count": len(encoded_durations),
        "requested_frame_rate_fps": FRAME_RATE,
        "requested_frame_period_ms": {"numerator": 1000, "denominator": FRAME_RATE},
        "encoded_frame_duration_counts_ms": {
            str(duration): duration_counts[duration] for duration in sorted(duration_counts)
        },
        "encoded_total_duration_ms": sum(encoded_durations),
        "gif_loop_count": loop_count,
        "motion": {
            "description": "The operator-supplied animation of the exact approved girl-plus-four-spirit square plays inside one fixed right-side window. The source artwork itself supplies the articulated dance; the composer adds no whole-image sway, bob, rotation, scale, or motion trail.",
            "sampling": "120 normalized source frames at 12 fps. Frames 12 through 107 are used in source order before the fixed crop, edge mask, and composition; 12 end-to-start crossfade frames close the loop, with the final blend preceding source frame 12.",
            "source_frame_count": SOURCE_FRAME_COUNT,
            "loop_blend_frames": LOOP_BLEND_FRAMES,
            "motion_window_xywh": [
                MASCOT_VISIBLE_POSITION[0],
                MASCOT_VISIBLE_POSITION[1],
                MASCOT_VISIBLE_SOURCE_BOX[2] - MASCOT_VISIBLE_SOURCE_BOX[0],
                MASCOT_VISIBLE_SOURCE_BOX[3] - MASCOT_VISIBLE_SOURCE_BOX[1],
            ],
            "motion_source_crop_xyxy": list(MASCOT_VISIBLE_SOURCE_BOX),
            "translation_pixels": [0, 0],
            "rotation_degrees": 0,
            "scale": 1,
            "character_source_edit": "none; the exact supplied animation frames are decoded and anchored without repainting or regeneration",
            "static_layout": "typography, labels, chips, cursor, particles, scanline texture, border, background, crop position, and safe-area geometry are phase-independent",
        },
        "pillow_version": PILLOW_VERSION,
        "ffmpeg_version": ffmpeg_version(),
        "gif_palette_max_colors": GIF_COLORS,
        "gif_dither": "none",
        "palette": PALETTE,
        "motion_source": GHOST_MOTION_SOURCE.name,
        "motion_source_sha256": sha256(GHOST_MOTION_SOURCE),
        "motion_source_dimensions": [MASCOT_SIZE, MASCOT_SIZE],
        "motion_source_frame_rate_fps": FRAME_RATE,
        "motion_source_frame_count": SOURCE_FRAME_COUNT,
        "motion_source_duration_ms": 10000,
        "motion_source_original_filename": "cute_Blackhatshiftey_Canticle-girl.mp4",
        "motion_source_original_sha256": "c75ef04a22da4baca549bd601f3490de0c28f1860b0d20e8fa77c0a48f85bf42",
        "motion_source_normalization": "primary H.264 video stream only; audio and attached cover art removed; 560x560, 12 fps, 120 frames, libx264 CRF 18",
        "source": GHOST_SOURCE.name,
        "source_sha256": sha256(GHOST_SOURCE),
        "source_origin": "local Canticle duo square batch slot 3",
        "source_lineage": "AnimagineXL 3.1, seed 20260820, batch slot 3",
        "source_dimensions": [1024, 1024],
        "source_sampler": "dpmpp_2m",
        "source_scheduler": "karras",
        "source_steps": 28,
        "source_cfg": 6.5,
        "source_prompt": "masterpiece, best quality, anime style, 1girl, ghost girl, cute kawaii spirit mascot, translucent glowing white body, big sparkling eyes, sweet smile, small cute ghost companion floating beside her, matching design, cute duo, two characters, floating pose, sparkling particles, stars, neon pink rim lighting, cyan glow, mint green accents, holographic shimmer, dark navy background, night palette, glowing, soft lighting, full body, centered composition",
        "source_negative_prompt": "lowres, bad anatomy, bad hands, text, error, missing fingers, fewer digits, cropped, worst quality, low quality, jpeg artifacts, signature, watermark, username, blurry, realistic, 3d, nsfw, nude, scary, grotesque",
        "cameo": CAMEO_OUT.name,
        "cameo_sha256": sha256(CAMEO_OUT),
        "png_sha256": sha256(PNG_OUT),
        "gif_sha256": sha256(GIF_OUT),
    }
    META_OUT.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"rendered {PNG_OUT.relative_to(ROOT)} ({WIDTH}x{HEIGHT})")
    print(f"rendered {GIF_OUT.relative_to(ROOT)} ({FRAME_COUNT} anchored motion frames)")
    print(f"rendered {CAMEO_OUT.relative_to(ROOT)}")
    print(f"wrote {META_OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
