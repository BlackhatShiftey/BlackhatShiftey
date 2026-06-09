from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math


WIDTH = 1000
HEIGHT = 260
OUT = Path("assets/terminal-banner.gif")

FONT_REGULAR = "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"

OPS_WORDS = [
    ("BUILD", "#46f4ff"),
    ("BREAK", "#f6dc7a"),
    ("FIX", "#ff674d"),
    ("BENCHMARK", "#c86bff"),
    ("IMPROVE", "#34f5c5"),
]

FRAMES_PER_WORD = 4
CURSOR_PERIOD = 5
CURSOR_ON_FRAMES = {0, 1}
EDGE_FLOW_COLORS = ["#46f4ff", "#f4f1ff", "#c86bff", "#34f5c5"]


def font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REGULAR, size)


def hex_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def lerp(a, b, t):
    return int(a + (b - a) * t)


def vertical_gradient(size, top, mid, bottom):
    img = Image.new("RGB", size)
    pix = img.load()
    top, mid, bottom = map(hex_rgb, (top, mid, bottom))
    split = size[1] * 0.52

    for y in range(size[1]):
        if y < split:
            t = y / split
            color = tuple(lerp(top[i], mid[i], t) for i in range(3))
        else:
            t = (y - split) / (size[1] - split)
            color = tuple(lerp(mid[i], bottom[i], t) for i in range(3))

        for x in range(size[0]):
            pix[x, y] = color

    return img


def text_size(draw, text, text_font):
    box = draw.textbbox((0, 0), text, font=text_font)
    return box[2] - box[0], box[3] - box[1]


def fit_font(draw, text, max_width, start_size, min_size=12):
    for size in range(start_size, min_size - 1, -1):
        candidate = font(size, bold=True)
        if text_size(draw, text, candidate)[0] <= max_width:
            return candidate
    return font(min_size, bold=True)


def add_glow(base, draw_fn, blur=7):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(layer))
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))


def edge_color(index):
    colors = [hex_rgb(color) for color in EDGE_FLOW_COLORS]
    return colors[index % len(colors)]


def rounded_border_points(x0, y0, x1, y1, radius, step=10):
    points = []

    for x in range(x0 + radius, x1 - radius + 1, step):
        points.append((x, y0))

    for degree in range(270, 361, 8):
        angle = math.radians(degree)
        points.append((x1 - radius + int(math.cos(angle) * radius), y0 + radius + int(math.sin(angle) * radius)))

    for y in range(y0 + radius, y1 - radius + 1, step):
        points.append((x1, y))

    for degree in range(0, 91, 8):
        angle = math.radians(degree)
        points.append((x1 - radius + int(math.cos(angle) * radius), y1 - radius + int(math.sin(angle) * radius)))

    for x in range(x1 - radius, x0 + radius - 1, -step):
        points.append((x, y1))

    for degree in range(90, 181, 8):
        angle = math.radians(degree)
        points.append((x0 + radius + int(math.cos(angle) * radius), y1 - radius + int(math.sin(angle) * radius)))

    for y in range(y1 - radius, y0 + radius - 1, -step):
        points.append((x0, y))

    for degree in range(180, 271, 8):
        angle = math.radians(degree)
        points.append((x0 + radius + int(math.cos(angle) * radius), y0 + radius + int(math.sin(angle) * radius)))

    return points


def draw_flowing_border(img, frame_index):
    points = rounded_border_points(2, 2, 997, 257, 22)
    segment_count = 30
    start = (frame_index * 7) % len(points)
    flow = [points[(start + offset) % len(points)] for offset in range(segment_count)]

    def draw_segment(draw, width, alpha):
        for i in range(len(flow) - 1):
            base = edge_color(i // 8)
            color = (*base, alpha)
            draw.line((*flow[i], *flow[i + 1]), fill=color, width=width)

    add_glow(img, lambda d: draw_segment(d, 7, 78), blur=4)
    draw_segment(ImageDraw.Draw(img), 3, 190)


def draw_text_glow(img, pos, text, text_font, fill, glow_fill, blur=2):
    add_glow(img, lambda d: d.text(pos, text, font=text_font, fill=glow_fill), blur)
    ImageDraw.Draw(img).text(pos, text, font=text_font, fill=fill)


def cursor_is_visible(frame_index):
    return frame_index % CURSOR_PERIOD in CURSOR_ON_FRAMES


def draw_frame(frame_index, word, color):
    img = Image.new("RGBA", (WIDTH, HEIGHT), (3, 5, 9, 255))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((0, 0, WIDTH - 1, HEIGHT - 1), radius=24, fill=(3, 5, 9, 255))

    glass = vertical_gradient((WIDTH - 2, HEIGHT - 2), "#17212a", "#080c12", "#030509").convert("RGBA")
    mask = Image.new("L", (WIDTH - 2, HEIGHT - 2), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, WIDTH - 3, HEIGHT - 3), radius=22, fill=255)
    img.paste(glass, (1, 1), mask)
    draw = ImageDraw.Draw(img)

    for x in range(1, WIDTH, 48):
        draw.line((x, 1, x, HEIGHT - 2), fill=(18, 63, 77, 255))
    for y in range(1, HEIGHT, 48):
        draw.line((1, y, WIDTH - 2, y), fill=(18, 63, 77, 255))

    draw.rounded_rectangle((2, 2, 997, 257), radius=22, outline=(244, 241, 255, 150), width=2)
    draw.rounded_rectangle((10, 10, 989, 249), radius=18, outline=(32, 40, 50, 255), width=1)
    draw.line((38, 73, 958, 73), fill=(32, 44, 52, 255), width=1)
    draw.line((38, 74, 958, 74), fill=(38, 135, 145, 255), width=1)

    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.polygon([(78, 22), (934, 22), (820, 72), (38, 72)], fill=(255, 255, 255, 28))
    overlay_draw.polygon([(704, 0), (1000, 0), (1000, 28), (650, 28)], fill=(255, 255, 255, 7))
    overlay_draw.polygon([(0, 218), (335, 218), (254, 260), (0, 260)], fill=(70, 244, 255, 8))
    img.alpha_composite(overlay)
    draw = ImageDraw.Draw(img)

    draw.ellipse((45, 37, 55, 47), fill=(200, 107, 255, 255))
    draw.ellipse((68, 37, 78, 47), fill=(70, 244, 255, 255))
    draw.ellipse((91, 37, 101, 47), fill=(52, 245, 197, 255))
    draw.text((128, 35), "root@blackhatshiftey:/ops", font=font(15), fill=(184, 199, 212, 255))

    draw.text((64, 94), "$ ./profile --signal", font=font(20), fill=(159, 248, 255, 255))
    if cursor_is_visible(frame_index):
        draw.rectangle((314, 96, 324, 118), fill=(159, 248, 255, 255))

    draw_text_glow(
        img,
        (64, 126),
        "BlackhatShiftey",
        font(50, bold=True),
        (255, 255, 255, 255),
        (255, 255, 255, 95),
        blur=2,
    )
    draw = ImageDraw.Draw(img)
    draw.text((66, 181), "AI Architect | Python | Security Automation", font=font(24), fill=(184, 199, 212, 255))

    panel = (760, 103, 930, 199)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(panel, radius=12, fill=(4, 9, 15, 255), outline=hex_rgb(color), width=2)
    draw.rounded_rectangle((768, 111, 922, 191), radius=9, fill=(7, 14, 22, 255), outline=(31, 42, 51, 255), width=1)
    draw.polygon([(772, 113), (920, 113), (884, 128), (768, 128)], fill=(20, 30, 39, 255))
    draw.text((778, 122), "OPS CYCLE", font=font(14), fill=(159, 248, 255, 255))

    word_font = fit_font(draw, word, 136, 29, min_size=19)
    word_width, _ = text_size(draw, word, word_font)
    word_x = 760 + (170 - word_width) // 2
    draw_text_glow(img, (word_x, 148), word, word_font, (255, 255, 255, 255), (*hex_rgb(color), 150), blur=2)

    draw = ImageDraw.Draw(img)
    draw.text((779, 181), "build -> improve", font=font(12), fill=(154, 169, 182, 255))
    draw.line((64, 229, 268, 229), fill=(70, 244, 255, 120), width=2)
    draw.line((268, 229, 286, 216), fill=(244, 241, 255, 120), width=2)
    draw.line((286, 216, 472, 216), fill=(200, 107, 255, 120), width=2)
    draw.line((472, 216, 490, 229), fill=(244, 241, 255, 120), width=2)
    draw.line((490, 229, 936, 229), fill=(52, 245, 197, 120), width=2)
    draw_flowing_border(img, frame_index)

    return img.convert("RGB")


def main():
    frames = []
    durations = []
    frame_index = 0

    for word, color in OPS_WORDS:
        for pulse in range(FRAMES_PER_WORD):
            frames.append(draw_frame(frame_index, word, color))
            durations.append(190 if pulse < FRAMES_PER_WORD - 1 else 520)
            frame_index += 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=durations, loop=0)
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes, {len(frames)} frames)")


if __name__ == "__main__":
    main()
