"""ONE DAY - ONE ORBIT: Tuesday 17 November 2026 in one picture.

A self-contained drawing program (Python standard library only) that
renders a dark mission-patch style poster summing up the world news of
Tuesday 17 November 2026 and writes it as a PNG image.

The poster leads with the day's biggest story - Ukraine's strike partly
collapsing the Kerch (Crimea) Bridge - and gives six more stories a tile
each: the Quad summit in Manila, Iranian drones over the Gulf, the UN's
Gaza winter warning, California's suit against OpenAI, the United States
losing its measles-elimination status, and the COP31 draft deal.

No network, no third-party packages: the pixels are plotted into a
framebuffer by hand and encoded as PNG with zlib.  The drawing uses no
clock and no unseeded randomness, so every run writes identical bytes.
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

# --- palette -------------------------------------------------------------
BG = (9, 12, 24)            # deep space navy
PANEL = (17, 23, 42)        # tile face
PANEL_EDGE = (64, 84, 128)  # tile border
INK = (233, 238, 248)       # headline white
DIM = (148, 163, 196)       # secondary text
GOLD = (242, 193, 84)
RED = (238, 96, 84)
CYAN = (96, 205, 224)
GREEN = (110, 214, 148)
ORANGE = (246, 150, 60)
YELLOW = (252, 214, 110)
WATER = (22, 54, 102)
WATER_LT = (44, 92, 150)
STEEL = (170, 182, 205)
STEEL_DK = (96, 110, 140)
SMOKE = (90, 100, 124)

# --- 5x7 bitmap font -----------------------------------------------------
# Each glyph is seven rows of five pixels; '#' plots, '.' skips.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", ".#.#.", "..#..", ".#.#.", ".#.#.", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "·": (".....", ".....", ".....", ".###.", ".###.", ".....", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", ".#.##", "#..##"),
}


# --- framebuffer ---------------------------------------------------------

def new_canvas():
    """A fresh framebuffer filled with the background colour."""
    return bytearray(bytes(BG) * (W * H))


def px(buf, x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i] = color[0]
        buf[i + 1] = color[1]
        buf[i + 2] = color[2]


def rect(buf, x0, y0, x1, y1, color):
    """Filled rectangle over [x0, x1) x [y0, y1), clipped to the canvas."""
    x0 = max(0, x0)
    y0 = max(0, y0)
    x1 = min(W, x1)
    y1 = min(H, y1)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(color) * (x1 - x0)
    for y in range(y0, y1):
        i = (y * W + x0) * 3
        buf[i:i + len(row)] = row


def circle(buf, cx, cy, r, color):
    """Filled circle."""
    for dy in range(-r, r + 1):
        dx = math.isqrt(r * r - dy * dy)
        rect(buf, cx - dx, cy + dy, cx + dx + 1, cy + dy + 1, color)


def ring(buf, cx, cy, r, color, thick=2):
    """Circle outline drawn as a band of radius r."""
    for dy in range(-r, r + 1):
        dx = math.isqrt(r * r - dy * dy)
        px(buf, cx - dx, cy + dy, color)
        px(buf, cx + dx, cy + dy, color)
    for dx in range(-r, r + 1):
        dy = math.isqrt(r * r - dx * dx)
        px(buf, cx + dx, cy - dy, color)
        px(buf, cx + dx, cy + dy, color)
    if thick > 1:
        ring(buf, cx, cy, r - 1, color, thick - 1)


def line(buf, x0, y0, x1, y1, width, color):
    """Thick straight line: stamps filled circles along the segment."""
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    rad = max(0, width // 2)
    for s in range(steps + 1):
        x = x0 + (x1 - x0) * s // steps
        y = y0 + (y1 - y0) * s // steps
        if rad == 0:
            px(buf, x, y, color)
        else:
            circle(buf, x, y, rad, color)


def poly_fill(buf, pts, color):
    """Scanline fill of a polygon given as (x, y) vertices."""
    ys = [p[1] for p in pts]
    n = len(pts)
    for y in range(min(ys), max(ys) + 1):
        xs = []
        for i in range(n):
            xa, ya = pts[i]
            xb, yb = pts[(i + 1) % n]
            if (ya <= y < yb) or (yb <= y < ya):
                xs.append(xa + (y - ya) * (xb - xa) // (yb - ya))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            rect(buf, xs[i], y, xs[i + 1] + 1, y + 1, color)


def star_pts(cx, cy, r_out, r_in, spikes, rot=-90):
    pts = []
    for i in range(2 * spikes):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180 / spikes)
        pts.append((cx + int(r * math.cos(a)), cy + int(r * math.sin(a))))
    return pts


# --- text ----------------------------------------------------------------

def text_width(s, scale, tracking):
    if not s:
        return 0
    return len(s) * (5 * scale + tracking) - tracking


def draw_text(buf, x, y, s, scale, color, tracking=None):
    """Draws s with its top-left at (x, y); returns the x just past it."""
    if tracking is None:
        tracking = scale
    for ch in s.upper():
        glyph = FONT.get(ch, FONT[" "])
        for gy, row in enumerate(glyph):
            for gx, cell in enumerate(row):
                if cell == "#":
                    rect(buf, x + gx * scale, y + gy * scale,
                         x + (gx + 1) * scale, y + (gy + 1) * scale, color)
        x += 5 * scale + tracking
    return x


def center_text(buf, y, s, scale, color, tracking=None):
    if tracking is None:
        tracking = scale
    x = (W - text_width(s, scale, tracking)) // 2
    draw_text(buf, x, y, s, scale, color, tracking)


def wrap(s, scale, tracking, max_w):
    """Greedy word wrap to lines no wider than max_w pixels."""
    lines = []
    cur = ""
    for word in s.split():
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale, tracking) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def panel(buf, x, y, w, h):
    rect(buf, x, y, x + w, y + h, PANEL)
    rect(buf, x, y, x + w, y + 2, PANEL_EDGE)
    rect(buf, x, y + h - 2, x + w, y + h, PANEL_EDGE)
    rect(buf, x, y, x + 2, y + h, PANEL_EDGE)
    rect(buf, x + w - 2, y, x + w, y + h, PANEL_EDGE)


# --- pictograms ----------------------------------------------------------

def icon_flag(buf, cx, cy):
    """A summit flag: pole, three stripes, one gold star."""
    rect(buf, cx - 26, cy - 30, cx - 23, cy + 30, STEEL)
    rect(buf, cx - 23, cy - 30, cx + 27, cy - 20, RED)
    rect(buf, cx - 23, cy - 20, cx + 27, cy - 10, INK)
    rect(buf, cx - 23, cy - 10, cx + 27, cy + 0, CYAN)
    poly_fill(buf, star_pts(cx - 14, cy - 20, 6, 3, 5), GOLD)
    rect(buf, cx - 30, cy + 28, cx + 30, cy + 31, STEEL_DK)


def icon_ship(buf, cx, cy):
    """A tanker in the strait, a spiked mine bobbing ahead of it."""
    rect(buf, cx - 30, cy + 14, cx + 28, cy + 20, WATER_LT)
    rect(buf, cx - 26, cy + 22, cx + 24, cy + 26, WATER_LT)
    hull = [(cx - 28, cy + 2), (cx + 26, cy + 2), (cx + 18, cy + 14),
            (cx - 20, cy + 14)]
    poly_fill(buf, hull, RED)
    rect(buf, cx - 20, cy - 8, cx - 6, cy + 2, STEEL)
    rect(buf, cx - 2, cy - 8, cx + 12, cy + 2, GOLD)
    rect(buf, cx + 14, cy - 14, cx + 17, cy + 2, STEEL)
    mx, my = cx + 24, cy + 22
    circle(buf, mx, my, 6, INK)
    for dx, dy in ((-8, 0), (8, 0), (0, -8), (0, 8),
                   (-6, -6), (6, -6), (-6, 6), (6, 6)):
        line(buf, mx, my, mx + dx, my + dy, 2, INK)


def icon_tent(buf, cx, cy):
    """A camp tent under falling snow: winter coming for the displaced."""
    tent = [(cx - 30, cy + 24), (cx, cy - 16), (cx + 30, cy + 24)]
    poly_fill(buf, tent, GOLD)
    door = [(cx - 9, cy + 24), (cx, cy + 2), (cx + 9, cy + 24)]
    poly_fill(buf, door, BG)
    rect(buf, cx - 32, cy + 24, cx + 32, cy + 27, STEEL_DK)
    for fx, fy in ((cx - 22, cy - 24), (cx + 4, cy - 28), (cx + 24, cy - 14)):
        for dx, dy in ((-6, 0), (6, 0), (0, -6), (0, 6),
                       (-4, -4), (4, -4), (-4, 4), (4, 4)):
            line(buf, fx, fy, fx + dx, fy + dy, 2, CYAN)


def icon_scales(buf, cx, cy):
    """Scales of justice for a first-of-its-kind lawsuit."""
    rect(buf, cx - 2, cy - 26, cx + 2, cy + 22, GOLD)
    rect(buf, cx - 26, cy - 26, cx + 26, cy - 23, GOLD)
    circle(buf, cx, cy - 26, 4, GOLD)
    for side in (-1, 1):
        px0 = cx + side * 22
        line(buf, px0, cy - 23, px0 - 8, cy - 6, 2, GOLD)
        line(buf, px0, cy - 23, px0 + 8, cy - 6, 2, GOLD)
        for dy in range(0, 7):
            half = 10 - dy
            rect(buf, px0 - half, cy - 6 + dy, px0 + half + 1,
                 cy - 5 + dy, GOLD)
    rect(buf, cx - 12, cy + 22, cx + 12, cy + 26, GOLD)


def icon_virus(buf, cx, cy):
    """A virus particle: the outbreak behind the measles headline."""
    for i in range(8):
        a = math.radians(i * 45)
        x1 = cx + int(17 * math.cos(a))
        y1 = cy + int(17 * math.sin(a))
        x2 = cx + int(26 * math.cos(a))
        y2 = cy + int(26 * math.sin(a))
        line(buf, x1, y1, x2, y2, 3, RED)
        circle(buf, x2, y2, 4, RED)
    circle(buf, cx, cy, 17, RED)
    for dx, dy in ((-7, -5), (6, -8), (0, 4), (9, 8), (-9, 9)):
        circle(buf, cx + dx, cy + dy, 3, ORANGE)


def icon_leaf(buf, cx, cy):
    """A leaf under a small sun: the climate draft deal."""
    for i in range(8):
        a = math.radians(i * 45 + 20)
        x1 = cx - 20 + int(11 * math.cos(a))
        y1 = cy - 18 + int(11 * math.sin(a))
        x2 = cx - 20 + int(17 * math.cos(a))
        y2 = cy - 18 + int(17 * math.sin(a))
        line(buf, x1, y1, x2, y2, 2, YELLOW)
    circle(buf, cx - 20, cy - 18, 9, YELLOW)
    # leaf blade: two arcs meeting in points at both ends
    pts = []
    for i in range(21):
        t = i / 20
        pts.append((cx - 24 + int(52 * t),
                    cy + 8 - int(15 * math.sin(math.pi * t))))
    for i in range(20, -1, -1):
        t = i / 20
        pts.append((cx - 24 + int(52 * t),
                    cy + 8 + int(9 * math.sin(math.pi * t))))
    poly_fill(buf, pts, GREEN)
    line(buf, cx - 24, cy + 8, cx + 28, cy + 8, 2, BG)
    line(buf, cx - 24, cy + 8, cx - 31, cy + 13, 3, GREEN)


# --- hero scene ----------------------------------------------------------

def hero_scene(buf):
    """The Kerch Bridge, struck: one span down in the strait."""
    # water and its wave ticks
    rect(buf, 52, 352, 972, 396, WATER)
    for i in range(26):
        wx = 66 + (i * 67) % 880
        wy = 362 + (i * 29) % 26
        rect(buf, wx, wy, wx + 16, wy + 2, WATER_LT)
    # pylons and suspension lines
    for px0 in (150, 420, 806):
        rect(buf, px0, 262, px0 + 8, 352, STEEL_DK)
    for base in (158, 428, 814):
        for k in range(1, 6):
            sx = base + k * 42
            if sx < 940:
                rect(buf, sx, 284, sx + 2, 318, STEEL_DK)
    # intact decks, left and right of the gap
    rect(buf, 64, 318, 556, 327, STEEL)
    rect(buf, 668, 318, 960, 327, STEEL)
    # the fallen span, tipped down into the water
    line(buf, 556, 322, 664, 358, 9, STEEL)
    line(buf, 618, 356, 692, 368, 8, STEEL_DK)
    # smoke rising from the hit, drifting right
    for sx, sy, sr in ((638, 278, 9), (666, 260, 13),
                       (700, 248, 10), (730, 240, 7)):
        circle(buf, sx, sy, sr, SMOKE)
    # blast burst where the span was hit
    poly_fill(buf, star_pts(600, 304, 30, 12, 8), ORANGE)
    circle(buf, 600, 304, 10, YELLOW)
    # incoming missile streak
    line(buf, 118, 250, 584, 298, 3, YELLOW)
    circle(buf, 118, 250, 4, ORANGE)
    # drones coming in from the right
    for dx0, dy0 in ((872, 258), (912, 278), (840, 284)):
        line(buf, dx0 - 7, dy0 - 7, dx0 + 7, dy0 + 7, 3, INK)
        line(buf, dx0 - 7, dy0 + 7, dx0 + 7, dy0 - 7, 3, INK)
        line(buf, dx0 - 16, dy0 + 14, dx0 - 7, dy0 + 5, 2, DIM)


# --- composition ---------------------------------------------------------

TILES = [
    ("MANILA · SUMMIT", GOLD, "TRUMP AT QUAD SUMMIT",
     "Quad meets in Manila; a US-China-Russia summit follows in Shenzhen.",
     icon_flag),
    ("HORMUZ · GULF", RED, "DRONES TARGET US BASE",
     "Iran drones target a US base in Bahrain; tanker hits a mine at Hormuz.",
     icon_ship),
    ("GAZA · AID", CYAN, "GAZA BRACES FOR WINTER",
     "UN warns of winter for 1.7M displaced; 4 nations demand open aid crossings.",
     icon_tent),
    ("CALIFORNIA · TECH", ORANGE, "CALIFORNIA SUES OPENAI",
     "The state AG sues over AI safety in a first case of its kind.",
     icon_scales),
    ("UNITED STATES · HEALTH", RED, "US LOSES MEASLES STATUS",
     "Elimination status lost after 26 years as cases pass a record 5,400.",
     icon_virus),
    ("ANTALYA · CLIMATE", GREEN, "COP31 DRAFT DEAL LANDS",
     "Antalya draft: faster fossil phase-out and $120bn in climate aid pledged.",
     icon_leaf),
]


def build():
    buf = new_canvas()
    # starfield: a fixed-seed scatter, so every run draws the same sky
    state = [20261117]

    def rnd(mod):
        state[0] = (1103515245 * state[0] + 12345) % 2147483648
        return state[0] % mod

    for _ in range(150):
        sx, sy = rnd(W), rnd(226)
        rect(buf, sx, sy, sx + 2, sy + 2, STEEL_DK if rnd(3) else DIM)
    # masthead
    center_text(buf, 34, "ONE DAY · ONE ORBIT", 3, GOLD, tracking=6)
    center_text(buf, 68, "TUESDAY", 12, INK, tracking=10)
    center_text(buf, 166, "17 NOVEMBER 2026", 5, CYAN, tracking=5)
    rect(buf, 36, 216, 988, 218, PANEL_EDGE)
    ring(buf, 512, 217, 9, GOLD, thick=1)
    circle(buf, 519, 210, 3, GOLD)
    # hero panel: the Kerch Bridge story
    panel(buf, 36, 232, 952, 288)
    hero_scene(buf)
    draw_text(buf, 56, 406, "UKRAINE · CRIMEA", 2, GOLD, tracking=3)
    draw_text(buf, 56, 428, "KERCH BRIDGE STRUCK", 5, INK, tracking=4)
    sub = wrap("Ukraine's strike partly collapses the Crimea bridge; "
               "Russia hits back at bridges in Kyiv.", 2, 1, 916)
    for i, ln in enumerate(sub):
        draw_text(buf, 56, 474 + i * 18, ln, 2, DIM, tracking=1)
    # six story tiles, two columns by three rows
    for idx, (kicker, accent, head, body, icon) in enumerate(TILES):
        tx = 36 + (idx % 2) * 486
        ty = 540 + (idx // 2) * 156
        panel(buf, tx, ty, 466, 140)
        icon(buf, tx + 410, ty + 46)
        draw_text(buf, tx + 16, ty + 12, kicker, 2, accent, tracking=3)
        head_lines = wrap(head, 3, 2, 330)
        for i, ln in enumerate(head_lines[:2]):
            draw_text(buf, tx + 16, ty + 36 + i * 26, ln, 3, INK, tracking=2)
        body_lines = wrap(body, 2, 1, 434)
        for i, ln in enumerate(body_lines[:2]):
            draw_text(buf, tx + 16, ty + 92 + i * 18, ln, 2, DIM, tracking=1)
    return buf


# --- PNG output ----------------------------------------------------------

def write_png(path, buf):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)
        raw += buf[y * stride:(y + 1) * stride]
    payload = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        return (struct.pack(">I", len(data)) + kind + data
                + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", payload) + chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(png)
    return len(png)


def output_path():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        return os.path.join(out_dir, "entry.png")
    if os.path.isdir("/output"):
        return "/output/entry.png"
    return "entry.png"


def main():
    buf = build()
    path = output_path()
    size = write_png(path, buf)
    print("wrote %s (%d bytes)" % (path, size))


if __name__ == "__main__":
    main()
