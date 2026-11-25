#!/usr/bin/env python3
"""news-image-20261125: one 1024x1024 front page summing up the world news
of Wednesday, 25 November 2026. Python 3.13, standard library only.

Draws everything from scratch on a raster canvas: a cream broadsheet with a
navy masthead, a lead illustration of the Baltic sea strike, and eight
verified stories of the day (Ukraine war at sea, the Houthi strike on
Riyadh, the CIA/ODNI hack, the Huawei verdict, COP31 ending with no deal,
the US inflation data due ahead of the Fed decision, the WHO Ebola
evacuation in DR Congo, and the Democrats clinching the US House), plus a
briefs ticker. No network, no clock, no randomness: two runs write
byte-identical PNG bytes.
"""

import os
import struct
import zlib
from binascii import crc32

W = 1024
H = 1024

PAPER = (247, 243, 232)
INK = (24, 24, 28)
NAVY = (18, 38, 74)
NAVY_LT = (38, 66, 112)
RED = (178, 39, 30)
GOLD = (196, 148, 56)
BLUE = (46, 92, 148)
SKY = (168, 200, 224)
SEA = (28, 68, 110)
TEAL = (32, 120, 110)
GREY = (112, 108, 98)
LIGHT = (233, 227, 211)
WHITE = (255, 255, 255)
ORANGE = (224, 110, 30)
DARK = (40, 40, 44)

# 5x7 bitmap font. Each glyph is 7 rows of 5 cells; '#' is on, '.' is off.
FONT = {
    "A": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "a": (".....", ".....", ".###.", "....#", ".####", "#...#", ".####"),
    "b": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    "c": (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    "d": ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    "e": (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    "f": ("..##.", ".#...", ".#...", "####.", ".#...", ".#...", ".#..."),
    "g": (".....", ".####", "#...#", "#...#", ".####", "....#", ".###."),
    "h": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "i": ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
    "j": ("...#.", ".....", "..##.", "...#.", "...#.", "...#.", "##..."),
    "k": ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    "l": (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "m": (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    "n": (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "o": (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    "p": (".....", "####.", "#...#", "#...#", "####.", "#....", "#...."),
    "q": (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    "r": (".....", ".....", "#.##.", "##...", "#....", "#....", "#...."),
    "s": (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    "t": (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
    "u": (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
    "v": (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "w": (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    "x": (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    "y": (".....", "#...#", "#...#", "#...#", ".####", "....#", ".###."),
    "z": (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".....", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "&": (".###.", "#...#", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "%": ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    "~": (".....", ".....", ".##.#", "#.#.#", ".....", ".....", "....."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    "[": (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    "]": (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
    "<": ("....#", "...#.", "..#..", ".#...", "..#..", "...#.", "....#"),
    ">": ("#....", ".#...", "..#..", "...#.", "..#..", ".#...", "#...."),
    "@": (".###.", "#...#", "#.###", "#.#.#", "#.##.", "#....", ".###."),
    "|": ("..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
}

# ---------------------------------------------------------------- canvas

class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def fill_rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def rect(self, x, y, w, h, c, t=1):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c, t=1):
        self.fill_rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill_rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def poly(self, pts, c):
        # Scanline fill of a simple polygon.
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if y0 == y1:
                    continue
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                xa = int(xs[k])
                xb = int(xs[k + 1])
                self.fill_rect(xa, y, xb - xa + 1, 1, c)

    def disc(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def ring(self, cx, cy, r, c, t=2):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            for xx in (cx - dx, cx + dx):
                for k in range(t):
                    self.set(xx - k if xx < cx else xx + k, cy + dy, c)

    # ------------------------------------------------------------ text
    def text_width(self, s, scale):
        return len(s) * 6 * scale

    def draw_text(self, x, y, s, c, scale=2, bold=False):
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT[" "])
            for ry in range(7):
                row = g[ry]
                for rx in range(5):
                    if row[rx] == "#":
                        self.fill_rect(cx + rx * scale, y + ry * scale,
                                       scale, scale, c)
                        if bold:
                            self.fill_rect(cx + rx * scale + 1,
                                           y + ry * scale, scale, scale, c)
            cx += 6 * scale
        return cx

    def text_center(self, x, y, w, s, c, scale=2, bold=False):
        tw = self.text_width(s, scale)
        self.draw_text(x + (w - tw) // 2, y, s, c, scale, bold)

    def wrap(self, s, width, scale):
        max_chars = max(1, width // (6 * scale))
        words = s.split(" ")
        lines = []
        cur = ""
        for wd in words:
            trial = wd if not cur else cur + " " + wd
            if len(trial) <= max_chars:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = wd
                while len(cur) > max_chars:
                    lines.append(cur[:max_chars])
                    cur = cur[max_chars:]
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, w, s, c, scale=2, leading=3, bold=False):
        lines = self.wrap(s, w, scale)
        for ln in lines:
            self.draw_text(x, y, ln, c, scale, bold)
            y += 7 * scale + leading
        return y


def png_bytes(cv):
    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", crc32(kind + data) & 0xFFFFFFFF)
        return out

    raw = bytearray()
    stride = cv.w * 3
    for yy in range(cv.h):
        raw.append(0)
        raw += cv.px[yy * stride:(yy + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
            + chunk(b"IEND", b""))

# ------------------------------------------------------------ illustrations

def draw_sea_scene(cv, x, y, w, h):
    # Sky in three bands, sun, then the sea.
    cv.fill_rect(x, y, w, h * 5 // 12, (196, 216, 232))
    cv.fill_rect(x, y + h * 5 // 12, w, h // 12, (178, 204, 226))
    cv.fill_rect(x, y + h // 2, w, h // 2, SEA)
    cv.disc(x + w - 52, y + 34, 22, GOLD)
    cv.disc(x + w - 52, y + 34, 16, (226, 182, 84))
    # Clouds.
    for cx, cy, r in ((x + 70, y + 30, 16), (x + 92, y + 26, 12),
                      (x + 220, y + 44, 13), (x + 240, y + 40, 10)):
        cv.disc(cx, cy, r, WHITE)
    # Distant horizon ship silhouette.
    cv.fill_rect(x + 300, y + h // 2 - 14, 60, 8, NAVY)
    cv.fill_rect(x + 318, y + h // 2 - 24, 8, 10, NAVY)
    # Cargo ship: hull, containers, funnel.
    hx, hy = x + 48, y + h // 2 + 22
    cv.poly([(hx, hy), (hx + 300, hy), (hx + 278, hy + 44),
             (hx + 22, hy + 44)], (52, 52, 58))
    cv.fill_rect(hx + 6, hy + 44, 288, 5, RED)
    cv.fill_rect(hx + 40, hy - 34, 44, 34, BLUE)
    cv.fill_rect(hx + 88, hy - 34, 44, 34, (178, 60, 40))
    cv.fill_rect(hx + 136, hy - 34, 44, 34, GOLD)
    cv.fill_rect(hx + 184, hy - 34, 44, 34, TEAL)
    cv.fill_rect(hx + 232, hy - 34, 44, 34, (120, 120, 128))
    cv.fill_rect(hx + 40, hy - 58, 44, 24, (178, 60, 40))
    cv.fill_rect(hx + 136, hy - 58, 44, 24, BLUE)
    cv.fill_rect(hx + 232, hy - 58, 44, 24, (90, 90, 98))
    cv.fill_rect(hx + 286, hy - 52, 16, 52, (30, 30, 34))
    cv.fill_rect(hx + 286, hy - 58, 16, 6, GOLD)
    # Blast and smoke above the stern.
    cv.disc(hx + 66, hy - 66, 16, ORANGE)
    cv.disc(hx + 66, hy - 66, 10, (250, 200, 60))
    cv.disc(hx + 52, hy - 84, 10, (120, 118, 112))
    cv.disc(hx + 70, hy - 98, 13, (140, 138, 130))
    cv.disc(hx + 92, hy - 92, 9, (120, 118, 112))
    # Drone above the bow, dashed track down to the blast.
    dx, dy = x + 300, y + 58
    cv.fill_rect(dx - 14, dy, 28, 6, DARK)
    cv.fill_rect(dx - 3, dy - 4, 6, 14, DARK)
    cv.fill_rect(dx - 26, dy - 3, 12, 3, DARK)
    cv.fill_rect(dx + 14, dy - 3, 12, 3, DARK)
    cv.disc(dx - 22, dy - 2, 5, (90, 90, 96))
    cv.disc(dx + 22, dy - 2, 5, (90, 90, 96))
    for k in range(0, 90, 12):
        cv.fill_rect(dx - 2 - k // 3, dy + 12 + k, 4, 6, RED)
    # Waves.
    for wy in (y + h - 58, y + h - 34, y + h - 12):
        for wx in range(x + 8, x + w - 8, 34):
            cv.line(wx, wy, wx + 17, wy - 7, (120, 170, 210))
            cv.line(wx + 17, wy - 7, wx + 34, wy, (120, 170, 210))
    cv.draw_text(x + 10, y + h - 20, "ILLUSTRATION: A DRONE STRIKE AT SEA",
                 (220, 230, 240), 1)


def draw_tower(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (222, 214, 196))
    cv.disc(x + w - 26, y + 14, 9, GOLD)
    base = y + h - 6
    # Tall tower with setbacks, windows, and a blast scar mid-height.
    cx = x + w // 2
    cv.fill_rect(cx - 32, y + 8, 64, base - y - 8, NAVY_LT)
    cv.fill_rect(cx - 24, y + 2, 48, 8, NAVY)
    for ry in range(y + 14, base - 5, 10):
        for rx in range(cx - 26, cx + 22, 9):
            cv.fill_rect(rx, ry, 5, 6, (200, 214, 228))
    mid = y + h // 2
    cv.poly([(cx - 32, mid - 5), (cx + 32, mid - 5),
             (cx + 20, mid + 11), (cx - 20, mid + 11)], ORANGE)
    cv.disc(cx, mid - 1, 9, (250, 200, 60))
    cv.disc(cx - 11, mid - 15, 7, (120, 118, 112))
    cv.disc(cx + 7, mid - 21, 9, (140, 138, 130))
    # Smaller neighbour towers, sitting on the same ground line.
    nh = h // 2
    cv.fill_rect(x + 18, base - nh, 40, nh, (150, 158, 168))
    cv.fill_rect(x + w - 58, base - nh, 40, nh, (150, 158, 168))
    cv.fill_rect(x, base, w, 6, (120, 114, 100))


def draw_server(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (26, 30, 44))
    # Two racks with blinking lights.
    for rx in (x + 14, x + w // 2 + 4):
        cv.fill_rect(rx, y + 8, w // 2 - 28, h - 16, (52, 58, 74))
        for ry in range(y + 14, y + h - 12, 12):
            cv.fill_rect(rx + 6, ry, w // 2 - 40, 6, (30, 34, 50))
            cv.disc(rx + w // 2 - 40, ry + 3, 2, (90, 220, 120))
            cv.disc(rx + w // 2 - 32, ry + 3, 2, RED)
    # Padlock in the middle.
    cx, cy = x + w // 2, y + h // 2
    cv.fill_rect(cx - 16, cy - 4, 32, 10, GOLD)
    cv.disc(cx, cy + 12, 16, GOLD)
    cv.disc(cx, cy + 12, 7, (26, 30, 44))
    cv.fill_rect(cx - 3, cy + 8, 6, 12, (26, 30, 44))
    cv.ring(cx, cy - 12, 14, GOLD, 3)


def draw_court(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, LIGHT)
    # Pediment and columns.
    cv.poly([(x + 14, y + 26), (x + w // 2, y + 4), (x + w - 14, y + 26)],
            NAVY)
    cv.fill_rect(x + 14, y + 26, w - 28, 5, NAVY)
    for cx in (x + 34, x + w // 2 - 4, x + w - 42):
        cv.fill_rect(cx, y + 34, 9, h - 44, NAVY)
    cv.fill_rect(x + 14, y + h - 12, w - 28, 6, NAVY)
    cv.fill_rect(x + w // 2 - 30, y + h - 34, 60, 22, RED)
    cv.draw_text(x + w // 2 - 24, y + h - 30, "GUILTY", WHITE, 1, True)


def draw_globe(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (214, 230, 226))
    cx, cy, r = x + w // 2, y + h // 2, h // 2 - 6
    cv.disc(cx, cy, r, BLUE)
    cv.disc(cx, cy, r - 3, (70, 140, 90))
    # Meridians and parallels.
    for dx in (-r // 2, 0, r // 2):
        cv.vline(cx + dx, cy - r + 4, 2 * r - 8, (200, 220, 210), 1)
    for dy in (-r // 2, 0, r // 2):
        cv.hline(cx - r + 4, cy + dy, 2 * r - 8, (200, 220, 210), 1)
    cv.ring(cx, cy, r, NAVY, 2)
    # Broken ring: the deal that did not close.
    cv.line(cx - r - 8, cy - r - 6, cx + r + 8, cy + r + 6, RED)
    cv.line(cx - r - 8, cy - r - 4, cx + r + 8, cy + r + 8, RED)
    cv.draw_text(x + 8, y + h - 12, "NO DEAL", RED, 1, True)


def draw_chart(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (238, 240, 236))
    oy = y + h - 14
    ox = x + 14
    cv.draw_text(x + 8, y + 6, "PCE DUE TODAY", RED, 1, True)
    # Candles across the panel, all inside it.
    bars = [(80, 12, RED), (108, 16, RED), (136, 8, TEAL),
            (164, 18, RED), (192, 10, TEAL), (220, 14, RED)]
    for bx, bh, col in bars:
        cv.fill_rect(ox + bx, oy - bh - 4, 14, bh, col)
        cv.vline(ox + bx + 7, oy - bh - 8, bh + 6, col, 1)
    cv.hline(ox, oy, w - 28, INK, 2)
    cv.vline(ox, y + 8, oy - y - 8, INK, 2)

# ---------------------------------------------------------------- layout

def kicker(cv, x, y, s):
    cv.fill_rect(x, y + 1, 8, 8, RED)
    cv.draw_text(x + 14, y, s, RED, 1, True)


def story_head(cv, x, y, w, s, scale):
    lines = cv.wrap(s, w, scale)
    for ln in lines:
        cv.draw_text(x, y, ln, INK, scale, True)
        y += 7 * scale + 3
    return y


def main():
    cv = Canvas(W, H, PAPER)
    cv.rect(8, 8, W - 16, H - 16, NAVY, 2)
    cv.rect(12, 12, W - 24, H - 24, NAVY, 1)

    # Masthead.
    cv.fill_rect(16, 16, W - 32, 112, NAVY)
    cv.draw_text(36, 36, "WORLD NEWS", (200, 214, 228), 1)
    cv.draw_text(W - 36 - cv.text_width("DAILY EDITION", 1), 36,
                 "DAILY EDITION", (200, 214, 228), 1)
    cv.text_center(16, 28, W - 32, "THE WORLD TODAY", WHITE, 6, True)
    cv.text_center(16, 82, W - 32, "WEDNESDAY, 25 NOVEMBER 2026",
                   GOLD, 2, True)
    cv.text_center(16, 108, W - 32,
                   "ONE DAY IN THE WORLD'S NEWS  -  EIGHT STORIES, ONE PAGE",
                   (200, 214, 228), 1)
    cv.fill_rect(16, 132, W - 32, 4, RED)

    # Lead story: Ukraine war at sea.
    draw_sea_scene(cv, 16, 140, 408, 296)
    tx, tw = 440, 568
    kicker(cv, tx, 146, "LEAD STORY  -  UKRAINE WAR AT SEA")
    y = story_head(cv, tx, 170, tw,
                   "Kyiv owns Baltic strike on Russian ship", 4)
    y = cv.para(tx, y + 8, tw,
                "President Volodymyr Zelenskiy confirms Ukraine was behind "
                "Saturday's drone strike on the Russian cargo ship Sparta II "
                "in the Gulf of Finland, calling the vessel a legitimate "
                "target because it was carrying weapons.",
                INK, 2, 3)
    y = cv.para(tx, y + 4, tw,
                "Kyiv also says it sank a Russian warship off Benghazi, "
                "Libya. Moscow calls the attacks terrorism and vows a "
                "response; Norway, a close ally, urges caution.",
                INK, 2, 3)
    cv.draw_text(tx, 414, "Sources: Reuters, Bloomberg", GREY, 1)

    cv.hline(16, 446, W - 32, NAVY, 2)
    cv.hline(16, 450, W - 32, RED, 1)

    # Row B: two half-page stories.
    draw_tower(cv, 16, 456, 488, 56)
    kicker(cv, 16, 520, "MIDDLE EAST  -  RIYADH")
    y = story_head(cv, 16, 536, 488,
                   "Houthis hit Riyadh's tallest tower again", 3)
    cv.para(16, y + 2, 488,
            "A drone strike wounds 11 at the wealth-fund tower, the second "
            "hit in a week. Riyadh vows a response.",
            INK, 2, 3)
    cv.vline(508, 456, 184, GREY, 1)
    draw_server(cv, 520, 456, 488, 56)
    kicker(cv, 520, 520, "CYBERSECURITY  -  WASHINGTON")
    y = story_head(cv, 520, 536, 488,
                   "CIA and ODNI hit by cyberattack", 3)
    cv.para(520, y + 2, 488,
            "Hackers breach an unclassified system for open-source work. "
            "Officials say no classified data was hit.",
            INK, 2, 3)

    cv.hline(16, 650, W - 32, NAVY, 2)

    # Row C: three columns.
    cols = [(16, "TECH  -  US COURT", "Huawei found guilty of stealing "
             "trade secrets",
             "A US jury convicts Huawei on 10 of 12 counts, including bank "
             "fraud. The firm rejects the verdict.", draw_court),
            (350, "CLIMATE  -  ANTALYA", "COP31 ends with no deal",
             "The UN summit in Antalya closes without agreement, split "
             "over fossil fuels. The first COP to fail since 2009.",
             draw_globe),
            (684, "MARKETS  -  WASHINGTON", "Inflation test looms as "
             "Nvidia rally fades",
             "US inflation and GDP data land today ahead of the Fed's "
             "December meeting. Gold slips.", draw_chart)]
    for i, (cx, kick, head, body, art) in enumerate(cols):
        if i:
            cv.vline(cx - 14, 660, 184, GREY, 1)
        art(cv, cx, 660, 320, 46)
        kicker(cv, cx, 714, kick)
        y = story_head(cv, cx, 730, 320, head, 2)
        cv.para(cx, y + 2, 320, body, INK, 2, 3)

    cv.hline(16, 854, W - 32, NAVY, 2)

    # Row D: two short stories.
    kicker(cv, 16, 866, "HEALTH  -  DR CONGO")
    y = story_head(cv, 16, 882, 488, "WHO pulls staff from Ebola hospital", 2)
    cv.para(16, y + 2, 488,
            "WHO staff leave an Ituri hospital after three days sheltering "
            "amid fighting.", INK, 2, 3)
    cv.vline(508, 864, 88, GREY, 1)
    kicker(cv, 520, 866, "POLITICS  -  WASHINGTON")
    y = story_head(cv, 520, 882, 488, "Democrats clinch the US House", 2)
    cv.para(520, y + 2, 488,
            "Democrats take at least 259 seats, their largest House "
            "majority since 1990.", INK, 2, 3)

    # Briefs ticker.
    cv.fill_rect(16, 962, W - 32, 30, NAVY)
    cv.text_center(16, 972, W - 32,
                   "ALSO: England level the T20 series vs Australia  -  "
                   "Trump pardons two turkeys  -  Sarkozy case goes to trial",
                   WHITE, 1)
    cv.text_center(16, 1000, W - 32,
                   "Sources: Reuters, Bloomberg, CNN, The New York Times, "
                   "AP, WHO, WRI  -  events reported on 25 November 2026",
                   GREY, 1)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "entry.png"), "wb") as fh:
        fh.write(png_bytes(cv))


if __name__ == "__main__":
    main()
