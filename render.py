#!/usr/bin/env python3
"""Render the Passport Page of a Country That Isn't There.

An invented passport spread for the Republic of Tidemere, a tidal
archipelago whose only land link is a causeway passable at low water.
Drawn from scratch with Pillow: no photos, no network, no randomness
(the same run always makes the same image).

The document is built to read as a real working passport:
  * one coherent layout, one palette, consistent type and margins;
  * every stamp, date and issue detail agrees: the passport was issued
    02 FEB 2024 and every stamp falls after that, before expiry
    01 FEB 2034; the Aldervik visa (issued 05 MAR 2024, valid to
    04 APR 2024) covers the 18-25 MAR 2024 trip exactly;
  * the holder is a licensed tide pilot of Port Lowick, so the portrait,
    the place-name and the tide paperwork all belong to the same place;
  * the telling detail is the tide itself: the causeway exit stamps
    record the low-water time, the tide table governs the crossings,
    and the endorsement says the holder may cross without escort.

Usage:  python3 render.py [v1|v2|v3] [out.png]
Default variant is v1.
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    """Load a DejaVu font, falling back through weights to the default."""
    for cand in (name, "DejaVuSans.ttf", "DejaVuSerif.ttf"):
        path = os.path.join(FONT_DIR, cand)
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default(size)


def F_serif(size):
    return font("DejaVuSerif.ttf", size)


def F_serif_b(size):
    return font("DejaVuSerif-Bold.ttf", size)


def F_serif_i(size):
    return font("DejaVuSerif-Italic.ttf", size)


def F_sans(size):
    return font("DejaVuSans.ttf", size)


def F_sans_b(size):
    return font("DejaVuSans-Bold.ttf", size)


def F_mono(size):
    return font("DejaVuSansMono.ttf", size)


# ---------------------------------------------------------------- ICAO MRZ
def _mrz_value(ch):
    if ch.isdigit():
        return int(ch)
    if ch == "<":
        return 0
    return ord(ch) - ord("A") + 10


def _check_digit(s):
    weights = (7, 3, 1)
    total = 0
    for i, ch in enumerate(s):
        total += _mrz_value(ch) * weights[i % 3]
    return str(total % 10)


def mrz_lines():
    """Two ICAO 9303 MRZ lines for Elena Maris Voss, TDM482913."""
    line1 = "P<TDM" + "VOSS<<ELENA<MARIS"
    line1 = line1 + "<" * (44 - len(line1))
    doc = "TDM482913"
    dob = "880314"          # 14 MAR 1988
    exp = "340201"          # 01 FEB 2034
    personal = "<" * 14
    body = (
        doc + _check_digit(doc)
        + "TDM"
        + dob + _check_digit(dob)
        + "F"
        + exp + _check_digit(exp)
        + personal + _check_digit(personal)
    )
    line2 = body + _check_digit(body)
    assert len(line1) == 44 and len(line2) == 44, (line1, line2)
    return line1, line2


# ---------------------------------------------------------------- helpers
def text(d, xy, s, fnt, fill, anchor="la"):
    d.text(xy, s, font=fnt, fill=fill, anchor=anchor)


def centred(d, cx, y, s, fnt, fill):
    text(d, (cx, y), s, fnt, fill, anchor="ma")


def rule(d, x0, x1, y, fill, width=1):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


def guilloche(d, box, colour, alpha=16):
    """Faint wavy security lines across a page."""
    x0, y0, x1, y1 = box
    layer = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for k in range(0, y1 - y0, 9):
        pts = []
        for x in range(0, x1 - x0, 8):
            pts.append((x, k + 3 * math.sin(x / 47.0 + k / 31.0)))
        ld.line(pts, fill=colour + (alpha,), width=1)
    for r in range(60, 560, 46):
        ld.arc([x1 - x0 - r, -r // 2, x1 - x0 + r, r * 2],
               90, 270, fill=colour + (alpha,), width=1)
    d._image.paste(layer, (x0, y0), layer)


def coat_of_arms(d, cx, cy, s, ink, gold, teal):
    """Shield: three waves, a lighthouse, one star. Plus motto handled
    by the caller."""
    w = s
    h = int(s * 1.18)
    x0, y0 = cx - w // 2, cy - h // 2
    # shield outline
    pts = [(x0, y0), (x0 + w, y0), (x0 + w, y0 + h - 12),
           (cx, y0 + h), (x0, y0 + h - 12)]
    d.polygon(pts, outline=ink, width=2)
    d.line([(x0 + 3, y0 + 3), (x0 + w - 3, y0 + 3),
            (x0 + w - 3, y0 + h - 13), (cx, y0 + h - 3),
            (x0 + 3, y0 + h - 13), (x0 + 3, y0 + 3)],
           fill=gold, width=1)
    # star above the shield
    sx, sy, r = cx, y0 - 9, 6
    star = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        star.append((sx + rr * math.cos(ang), sy + rr * math.sin(ang)))
    d.polygon(star, fill=gold)
    # lighthouse: tower + lamp + beams
    tx = cx
    ty = y0 + h - 34
    d.polygon([(tx - 5, ty + 22), (tx - 3, ty), (tx + 3, ty),
               (tx + 5, ty + 22)], fill=ink)
    d.rectangle([tx - 6, ty - 6, tx + 6, ty], fill=ink)
    d.ellipse([tx - 4, ty - 11, tx + 4, ty - 4], fill=gold)
    d.line([(tx - 7, ty - 8), (tx - 20, ty - 14)], fill=gold, width=2)
    d.line([(tx + 7, ty - 8), (tx + 20, ty - 14)], fill=gold, width=2)
    # three waves
    for j, wy in enumerate((y0 + h - 22, y0 + h - 15, y0 + h - 8)):
        pts = []
        for x in range(x0 + 6, x0 + w - 5, 4):
            pts.append((x, wy + 2 * math.sin((x - x0) / 9.0 + j)))
        d.line(pts, fill=teal, width=2)


def draw_portrait(d, box, pal):
    """Flat-style official portrait: Elena Maris Voss, tide pilot of
    Port Lowick. Drawn, not photographed, in the document's palette."""
    x, y, w, h = box
    d.rectangle([x, y, x + w, y + h], fill=pal["photo_bg"])
    # faint guilloche ring behind the head
    cx, cy = x + w // 2, y + int(h * 0.36)
    for r in range(46, 78, 8):
        d.ellipse([cx - r, cy - r, cx + r, cy + r],
                  outline=pal["photo_ring"], width=1)
    skin = pal["skin"]
    hair = pal["hair"]
    sweater = pal["sweater"]
    # shoulders / sweater
    d.polygon([(x + 8, y + h), (x + w - 8, y + h),
               (x + w - 18, y + int(h * 0.66)), (x + 18, y + int(h * 0.66))],
              fill=sweater)
    # cream collar
    d.polygon([(x + w // 2 - 26, y + int(h * 0.66)),
               (x + w // 2 + 26, y + int(h * 0.66)),
               (x + w // 2 + 14, y + int(h * 0.74)),
               (x + w // 2 - 14, y + int(h * 0.74))], fill=pal["paper"])
    # neck
    d.rectangle([cx - 13, y + int(h * 0.52), cx + 13, y + int(h * 0.68)],
                fill=pal["skin_dark"])
    # face
    d.ellipse([cx - 34, y + int(h * 0.10), cx + 34, y + int(h * 0.52)],
              fill=skin)
    # hair: swept top, sides, low bun
    d.pieslice([cx - 38, y + int(h * 0.02), cx + 38, y + int(h * 0.42)],
               180, 360, fill=hair)
    d.polygon([(cx - 38, y + int(h * 0.20)), (cx - 30, y + int(h * 0.20)),
               (cx - 33, y + int(h * 0.46)), (cx - 40, y + int(h * 0.42))],
              fill=hair)
    d.polygon([(cx + 38, y + int(h * 0.20)), (cx + 30, y + int(h * 0.20)),
               (cx + 33, y + int(h * 0.46)), (cx + 40, y + int(h * 0.42))],
              fill=hair)
    d.ellipse([cx - 14, y + int(h * 0.02) - 8, cx + 14, y + int(h * 0.02) + 16],
              fill=hair)
    # brows, eyes, nose, mouth -- minimal, symmetrical
    eb = pal["ink"]
    d.line([(cx - 24, y + int(h * 0.30)), (cx - 10, y + int(h * 0.295))],
           fill=eb, width=2)
    d.line([(cx + 10, y + int(h * 0.295)), (cx + 24, y + int(h * 0.30))],
           fill=eb, width=2)
    d.ellipse([cx - 21, y + int(h * 0.325), cx - 13, y + int(h * 0.345)],
              fill=eb)
    d.ellipse([cx + 13, y + int(h * 0.325), cx + 21, y + int(h * 0.345)],
              fill=eb)
    d.line([(cx, y + int(h * 0.35)), (cx - 2, y + int(h * 0.42))],
           fill=pal["skin_dark"], width=2)
    d.line([(cx - 9, y + int(h * 0.465)), (cx + 9, y + int(h * 0.465))],
           fill=pal["lip"], width=2)
    # light shading on one cheek
    d.arc([cx - 34, y + int(h * 0.10), cx + 34, y + int(h * 0.52)],
          200, 330, fill=pal["skin_dark"], width=2)
    d.rectangle([x, y, x + w, y + h], outline=pal["ink"], width=2)


def stamp_rect(d, box, lines, colour, angle, size=13, gap=15):
    """A rectangular ink stamp, drawn on its own layer and rotated."""
    x, y, w, h = box
    layer = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.rectangle([20, 20, 20 + w, 20 + h], outline=colour + (235,), width=3)
    ld.rectangle([25, 25, 20 + w - 5, 20 + h - 5],
                 outline=colour + (235,), width=1)
    fnt = F_sans_b(size)
    fnt2 = F_sans(size - 1)
    total = len(lines) * gap
    cy = 20 + (h - total) // 2 + size // 2
    for i, ln in enumerate(lines):
        f = fnt if i == 0 else fnt2
        ld.text((20 + w // 2, cy + i * gap), ln, font=f,
                fill=colour + (235,), anchor="ma")
    layer = layer.rotate(angle, resample=Image.BICUBIC, expand=False)
    d._image.paste(layer, (x - 20, y - 20), layer)


def stamp_round(d, cx, cy, r, lines, colour, angle):
    """A circular ink stamp."""
    layer = Image.new("RGBA", (2 * r + 40, 2 * r + 40), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    c = r + 20
    ld.ellipse([20, 20, 20 + 2 * r, 20 + 2 * r],
               outline=colour + (230,), width=3)
    ld.ellipse([28, 28, 20 + 2 * r - 8, 20 + 2 * r - 8],
               outline=colour + (230,), width=1)
    fnt = F_sans_b(12)
    fnt2 = F_sans(10)
    y = c - len(lines) * 8
    for i, ln in enumerate(lines):
        f = fnt if i == 1 else fnt2
        ld.text((c, y + i * 16), ln, font=f, fill=colour + (230,),
                anchor="ma")
    layer = layer.rotate(angle, resample=Image.BICUBIC, expand=False)
    d._image.paste(layer, (cx - r - 20, cy - r - 20), layer)


def draw_map(d, box, pal):
    """Small chart of the Tidemere Isles with the ferry route."""
    x, y, w, h = box
    ink, teal = pal["ink"], pal["accent"]
    d.rectangle([x, y, x + w, y + h], outline=ink, width=1)
    centred(d, x + w // 2, y + 6, "CHART — THE ISLES", F_sans_b(9), ink)
    # sea: faint horizontal lines
    for yy in range(y + 30, y + h - 8, 12):
        d.line([(x + 8, yy), (x + w - 8, yy)], fill=pal["photo_ring"],
               width=1)
    # three islands
    d.polygon([(x + 28, y + 96), (x + 52, y + 62), (x + 86, y + 70),
               (x + 96, y + 98), (x + 66, y + 118), (x + 38, y + 112)],
              outline=teal, width=2)
    d.polygon([(x + 118, y + 52), (x + 138, y + 34), (x + 162, y + 44),
               (x + 158, y + 66), (x + 132, y + 70)],
              outline=teal, width=2)
    d.polygon([(x + 130, y + 108), (x + 150, y + 92), (x + 172, y + 100),
               (x + 168, y + 122), (x + 142, y + 124)],
              outline=teal, width=2)
    # lighthouse on Lowick (largest isle)
    lx, ly = x + 62, y + 88
    d.polygon([(lx - 3, ly + 6), (lx - 2, ly - 8), (lx + 2, ly - 8),
               (lx + 3, ly + 6)], fill=ink)
    d.ellipse([lx - 3, ly - 12, lx + 3, ly - 6], fill=pal["gold"])
    # dotted ferry route
    for t in range(0, 21):
        fx = x + 62 + (138 - 62) * t / 20.0
        fy = y + 88 + (52 - 88) * t / 20.0 - 8 * math.sin(t / 20.0 * math.pi)
        d.ellipse([fx - 1.5, fy - 1.5, fx + 1.5, fy + 1.5], fill=teal)
    for t in range(0, 21):
        fx = x + 138 + (150 - 138) * t / 20.0
        fy = y + 52 + (108 - 52) * t / 20.0 + 6 * math.sin(t / 20.0 * math.pi)
        d.ellipse([fx - 1.5, fy - 1.5, fx + 1.5, fy + 1.5], fill=teal)
    text(d, (x + 10, y + h - 16), "LOWICK", F_sans_b(9), ink)
    text(d, (x + 112, y + 20), "MERROW", F_sans_b(9), ink)
    text(d, (x + 126, y + h - 16), "KETTLE ROCK", F_sans_b(9), ink)
    # compass
    ccx, ccy = x + w - 22, y + 44
    d.ellipse([ccx - 10, ccy - 10, ccx + 10, ccy + 10],
              outline=ink, width=1)
    d.polygon([(ccx, ccy - 9), (ccx - 3, ccy + 3), (ccx + 3, ccy + 3)],
              fill=ink)
    text(d, (ccx - 3, ccy - 20), "N", F_sans_b(9), ink)


def draw_tide_table(d, box, pal):
    """The tide table: the causeway opens around low water only."""
    x, y, w, h = box
    ink = pal["ink"]
    d.rectangle([x, y, x + w, y + h], outline=ink, width=1)
    centred(d, x + w // 2, y + 6, "TIDE TABLE — PORT LOWICK",
            F_sans_b(9), ink)
    rule(d, x + 8, x + w - 8, y + 24, ink)
    rows = [
        ("17 MAR 2024", "LW 05:02", "OPEN 04:17–05:47"),
        ("08 JUN 2024", "LW 04:31", "OPEN 03:46–05:16"),
        ("22 JUN 2024", "LW 04:48", "OPEN 04:03–05:33"),
    ]
    yy = y + 30
    for a, b, c in rows:
        text(d, (x + 10, yy), a, F_sans_b(11), ink)
        text(d, (x + 10, yy + 15), b, F_sans(11), ink)
        text(d, (x + w - 8, yy + 7), c, F_sans(10), ink, anchor="ra")
        yy += 30
    rule(d, x + 8, x + w - 8, y + h - 28, ink)
    centred(d, x + w // 2, y + h - 21,
            "CAUSEWAY PASSABLE ±45 MIN OF LOW WATER",
            F_sans(7), ink)


# ---------------------------------------------------------------- palettes
PALETTES = {
    "v1": dict(desk=(43, 58, 64), page=(246, 241, 227), ink=(29, 43, 42),
               accent=(21, 94, 87), gold=(168, 130, 47),
               navy=(34, 72, 110), burgundy=(124, 45, 43),
               green=(47, 107, 76), teal_stamp=(22, 96, 90),
               photo_bg=(201, 212, 210), photo_ring=(150, 165, 160),
               skin=(217, 169, 134), skin_dark=(190, 140, 108),
               hair=(58, 42, 34), sweater=(46, 95, 91), lip=(150, 90, 80),
               paper=(246, 241, 227)),
    "v2": dict(desk=(59, 45, 40), page=(249, 244, 231), ink=(42, 33, 28),
               accent=(124, 45, 43), gold=(150, 116, 42),
               navy=(38, 66, 96), burgundy=(124, 45, 43),
               green=(58, 96, 66), teal_stamp=(42, 92, 86),
               photo_bg=(214, 205, 190), photo_ring=(168, 152, 130),
               skin=(222, 176, 140), skin_dark=(196, 146, 112),
               hair=(52, 36, 28), sweater=(124, 45, 43), lip=(152, 92, 82),
               paper=(249, 244, 231)),
    "v3": dict(desk=(39, 47, 62), page=(243, 241, 233), ink=(32, 36, 46),
               accent=(34, 64, 107), gold=(154, 123, 46),
               navy=(34, 64, 107), burgundy=(122, 48, 52),
               green=(44, 96, 74), teal_stamp=(34, 88, 110),
               photo_bg=(196, 205, 216), photo_ring=(146, 158, 172),
               skin=(214, 166, 132), skin_dark=(188, 138, 106),
               hair=(44, 34, 30), sweater=(34, 64, 107), lip=(148, 88, 80),
               paper=(243, 241, 233)),
}


def render(variant="v1"):
    pal = PALETTES[variant]
    img = Image.new("RGB", (W, H), pal["desk"])
    d = ImageDraw.Draw(img, "RGBA")
    ink, accent, gold = pal["ink"], pal["accent"], pal["gold"]

    # ---- the open passport: two pages with a spine shadow
    LX, RX, TY, BY = 30, 524, 96, 928
    PW = 470
    d.rectangle([LX + 6, TY + 8, LX + PW + 6, BY + 8], fill=(0, 0, 0, 90))
    d.rectangle([RX + 6, TY + 8, RX + PW + 6, BY + 8], fill=(0, 0, 0, 90))
    d.rectangle([LX, TY, LX + PW, BY], fill=pal["page"])
    d.rectangle([RX, TY, RX + PW, BY], fill=pal["page"])
    d.rectangle([LX + PW - 4, TY, RX + 4, BY], fill=(0, 0, 0, 55))
    guilloche(d, (LX, TY, LX + PW, BY), pal["accent"], 13)
    guilloche(d, (RX, TY, RX + PW, BY), pal["accent"], 13)
    # faint lighthouse watermark on the data page
    wm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wm)
    wd.ellipse([RX + 330, TY + 560, RX + 430, TY + 660],
               outline=pal["accent"] + (22,), width=2)
    wd.polygon([(RX + 378, TY + 600), (RX + 374, TY + 560),
                (RX + 382, TY + 560)], fill=pal["accent"] + (22,))
    img.paste(wm, (0, 0), wm)
    d = ImageDraw.Draw(img, "RGBA")

    # ================================================= LEFT PAGE: visas
    cx = LX + PW // 2
    centred(d, cx, TY + 18, "VISAS", F_serif_b(24), ink)
    centred(d, cx, TY + 50, "VISA  ·  ENDORSEMENTS", F_sans(10), ink)
    rule(d, LX + 24, LX + PW - 24, TY + 70, gold, 2)
    rule(d, LX + 24, LX + PW - 24, TY + 74, ink, 1)

    draw_map(d, (LX + 24, TY + 88, 200, 150), pal)
    draw_tide_table(d, (LX + 236, TY + 88, 210, 150), pal)

    # Aldervik tideway visa
    stamp_rect(d, (LX + 24, TY + 254, 422, 92),
               ["KINGDOM OF ALDERVIK — TIDEWAY VISA",
                "SINGLE ENTRY  ·  ISSUED 05 MAR 2024  ·  VALID TO 04 APR 2024",
                "CONDITION: REGISTER WITH THE HARBOURMASTER",
                "WITHIN ONE DAY OF LANDING"],
               pal["burgundy"], -1.5, size=12, gap=15)

    # the travel history: every stamp after issue (02 FEB 2024)
    stamps = [
        (["PORT LOWICK", "DEPARTURE  ·  17 MAR 2024", "CAUSEWAY · LW 05:02"],
         pal["teal_stamp"], -5),
        (["ALDERVIK", "ARRIVAL  ·  18 MAR 2024", ""], pal["navy"], 4),
        (["ALDERVIK", "DEPARTURE  ·  25 MAR 2024", ""], pal["navy"], -3),
        (["PORT LOWICK", "ARRIVAL  ·  26 MAR 2024", "CAUSEWAY · LW 04:37"],
         pal["teal_stamp"], 6),
        (["PORT LOWICK", "DEPARTURE  ·  08 JUN 2024", "CAUSEWAY · LW 04:31"],
         pal["teal_stamp"], -4),
        (["KESSIG", "ARRIVAL  ·  09 JUN 2024", ""], pal["green"], 5),
        (["KESSIG", "DEPARTURE  ·  21 JUN 2024", ""], pal["green"], -6),
        (["PORT LOWICK", "ARRIVAL  ·  22 JUN 2024", "CAUSEWAY · LW 04:48"],
         pal["teal_stamp"], 3),
    ]
    sy = TY + 362
    for i, (lines, colour, ang) in enumerate(stamps):
        col = i % 2
        row = i // 2
        bx = LX + 24 + col * 213
        by = sy + row * 72
        lines = [ln for ln in lines if ln]
        stamp_rect(d, (bx, by, 205, 60), lines, colour, ang,
                   size=12, gap=14)

    # ferry levy + endorsement
    stamp_round(d, LX + 78, TY + 700, 52,
                ["FERRY LEVY", "12 CR", "PAID", "PORT LOWICK"],
                pal["burgundy"], -8)
    ex = LX + 150
    ey = TY + 664
    text(d, (ex, ey), "ENDORSEMENT", F_sans_b(11), ink)
    rule(d, ex, LX + PW - 24, ey + 18, gold, 1)
    endorse = ("HOLDER IS A LICENSED TIDE PILOT AND MAY CROSS "
               "THE CAUSEWAY WITHOUT ESCORT.")
    words, lines, cur = endorse.split(), [], ""
    for wd in words:
        if len(cur) + len(wd) + 1 <= 34:
            cur = (cur + " " + wd).strip()
        else:
            lines.append(cur)
            cur = wd
    lines.append(cur)
    for j, ln in enumerate(lines):
        text(d, (ex, ey + 26 + j * 15), ln, F_serif_i(12), ink)
    text(d, (LX + 24, BY - 26), "4", F_sans(10), ink)

    # ================================================= RIGHT PAGE: data
    cx = RX + PW // 2
    centred(d, cx, TY + 18, "REPUBLIC OF TIDEMERE", F_serif_b(26), ink)
    centred(d, cx, TY + 52, "P A S S P O R T", F_sans_b(14), ink)
    centred(d, cx, TY + 72, "PASSEPORT", F_serif_i(11), ink)
    coat_of_arms(d, cx, TY + 132, 50, ink, gold, accent)
    centred(d, cx, TY + 172, "·  THE TIDE PROVIDES  ·", F_serif_i(12), ink)
    rule(d, RX + 24, RX + PW - 24, TY + 194, gold, 2)
    rule(d, RX + 24, RX + PW - 24, TY + 198, ink, 1)

    # portrait + photo stamp
    photo = (RX + 24, TY + 214, 150, 188)
    draw_portrait(d, photo, pal)
    stamp_round(d, photo[0] + photo[2] - 16, photo[1] + photo[3] - 16, 30,
                ["PORT LOWICK", "02 FEB", "2024"], pal["burgundy"], 12)

    # type / code / number beside the photo
    fx = RX + 190
    fy = TY + 214
    for label, val, dx in (("TYPE", "P", 0), ("CODE", "TDM", 74),
                           ("No.", "TDM 482 913", 148)):
        text(d, (fx + dx, fy), label, F_sans(9), accent)
        text(d, (fx + dx, fy + 13), val, F_serif_b(15), ink)
    text(d, (fx, fy + 44), "NATIONALITY", F_sans(9), accent)
    text(d, (fx, fy + 57), "TIDEMERIAN", F_serif_b(15), ink)
    text(d, (fx, fy + 88), "OCCUPATION", F_sans(9), accent)
    text(d, (fx, fy + 101), "TIDE PILOT", F_serif_b(15), ink)
    text(d, (fx, fy + 132), "SEX", F_sans(9), accent)
    text(d, (fx, fy + 145), "F", F_serif_b(15), ink)

    # data grid
    fields = [
        ("SURNAME", "VOSS", "GIVEN NAMES", "ELENA MARIS"),
        ("DATE OF BIRTH", "14 MAR 1988", "PLACE OF BIRTH", "PORT LOWICK"),
        ("DATE OF ISSUE", "02 FEB 2024", "DATE OF EXPIRY", "01 FEB 2034"),
        ("SEX", "F", "NATIONALITY", "TIDEMERIAN"),
    ]
    gy = TY + 424
    for i, (l1, v1, l2, v2) in enumerate(fields):
        yy = gy + i * 52
        for label, val, xx in ((l1, v1, RX + 24), (l2, v2, RX + 256)):
            text(d, (xx, yy), label, F_sans(9), accent)
            text(d, (xx, yy + 13), val, F_serif_b(16), ink)
        rule(d, RX + 24, RX + PW - 24, yy + 40, pal["photo_ring"], 1)

    ay = TY + 640
    text(d, (RX + 24, ay), "AUTHORITY", F_sans(9), accent)
    text(d, (RX + 24, ay + 13), "MINISTRY OF THE TIDE — PORT LOWICK",
         F_serif_b(15), ink)
    # holder's signature
    sy = TY + 690
    text(d, (RX + 24, sy), "Elena Maris Voss", F_serif_i(21), ink)
    rule(d, RX + 24, RX + 250, sy + 30, ink, 1)
    text(d, (RX + 24, sy + 36), "HOLDER'S SIGNATURE", F_sans(9), accent)

    # machine-readable zone
    mz = (RX + 24, TY + 748, RX + 24 + 422, TY + 748 + 56)
    d.rectangle(mz, fill=(255, 255, 255, 110), outline=ink, width=1)
    l1, l2 = mrz_lines()
    text(d, (mz[0] + 10, mz[1] + 7), l1, F_mono(15), ink)
    text(d, (mz[0] + 10, mz[1] + 30), l2, F_mono(15), ink)
    centred(d, cx, BY - 26,
            "THIS PASSPORT IS THE PROPERTY OF THE REPUBLIC OF TIDEMERE",
            F_sans(8), ink)
    text(d, (RX + PW - 24, BY - 26), "5", F_sans(10), ink, anchor="ra")

    return img


def main():
    variant = sys.argv[1] if len(sys.argv) > 1 else "v1"
    out = sys.argv[2] if len(sys.argv) > 2 else f"variant-{variant}.png"
    if variant not in PALETTES:
        print(f"unknown variant {variant!r}, want one of "
              f"{sorted(PALETTES)}", file=sys.stderr)
        return 2
    img = render(variant)
    img.save(out, "PNG", optimize=True)
    size = os.path.getsize(out)
    print(f"{variant}: wrote {out} {img.size[0]}x{img.size[1]} "
          f"{size} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
