#!/usr/bin/env python3
"""Render v4 of the Tidemere passport spread (rebuild vs v1).

Same holder, same dates, same MRZ -- every consistency rule from v1
still holds (issue 02 FEB 2024, all stamps after issue, Aldervik visa
covers the 18-25 MAR trip, Kessig visa covers the 09-21 JUN trip,
valid ICAO check digits). What changes vs v1:

  * a redrawn portrait: shaded skin, arched brows, real eyes with
    iris + highlight, shaped lips, centre-part hair with side strands
    and a bun, V-neck sweater with a gold anchor pin;
  * no duplicated fields: the data grid's last row is now
    HEIGHT / EYES instead of a second SEX / NATIONALITY;
  * two visa boxes side by side (Aldervik + Kessig) instead of one,
    with a round Kessig harbour stamp overlapping the second box;
  * the dead space at the foot of the visa page is filled by
    spreading the travel stamps and adding the harbourmaster's
    caption line (a tide-curve chart was tried and cut: it did
    not fit the page and its axis came out inverted);
  * a fingerprint whorl beside the signature;
  * a thin double frame on each page, and display type
    (Crimson Pro / IBM Plex Serif / Instrument Sans) instead of
    DejaVu throughout.

Usage: python3 render_v4.py [out.png]   (default: variant-v4.png)
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R  # noqa: E402  (reuse MRZ, stamps, map, tide table, arms)

W, H = 1024, 1024
FONT_DIR = "/home/hatch/workspace/custom-skills/canvas-design/canvas-fonts"


def _font(name, size):
    path = os.path.join(FONT_DIR, name)
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return R.font("DejaVuSerif.ttf", size)


def F_head(size):
    return _font("CrimsonPro-Bold.ttf", size)


def F_serifb(size):
    return _font("IBMPlexSerif-Bold.ttf", size)


def F_serifi(size):
    return _font("IBMPlexSerif-Italic.ttf", size)


def F_sans(size):
    return _font("InstrumentSans-Regular.ttf", size)


def F_sansb(size):
    return _font("InstrumentSans-Bold.ttf", size)


def F_mono(size):
    return _font("IBMPlexMono-Regular.ttf", size)


PAL = dict(
    desk=(38, 52, 58), page=(247, 242, 228), ink=(26, 42, 40),
    accent=(18, 88, 82), gold=(158, 122, 44), navy=(32, 68, 104),
    burgundy=(122, 44, 42), green=(46, 102, 72),
    teal_stamp=(22, 96, 90), photo_bg=(204, 214, 212),
    photo_ring=(150, 165, 160), skin=(219, 172, 136),
    skin_dark=(186, 138, 106), skin_light=(232, 190, 156),
    hair=(56, 40, 32), hair_dark=(38, 26, 20), sweater=(36, 86, 82),
    lip=(146, 84, 76), lip_dark=(122, 62, 58), paper=(247, 242, 228),
)


def text(d, xy, s, fnt, fill, anchor="la"):
    d.text(xy, s, font=fnt, fill=fill, anchor=anchor)


def centred(d, cx, y, s, fnt, fill):
    text(d, (cx, y), s, fnt, fill, anchor="ma")


def rule(d, x0, x1, y, fill, width=1):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


def frame(d, box, pal):
    x0, y0, x1, y1 = box
    d.rectangle([x0 + 9, y0 + 9, x1 - 9, y1 - 9],
                outline=pal["gold"], width=1)
    d.rectangle([x0 + 13, y0 + 13, x1 - 13, y1 - 13],
                outline=pal["ink"], width=1)


# ---------------------------------------------------------------- portrait
def draw_portrait_v4(d, box, pal):
    x, y, w, h = box
    # background: soft vertical gradient + guilloche rings
    for yy in range(h):
        t = yy / max(h - 1, 1)
        c = tuple(int(pal["photo_bg"][i] + (176 - pal["photo_bg"][i]) * t)
                  for i in range(3))
        d.line([(x, y + yy), (x + w, y + yy)], fill=c)
    cx, cy = x + w // 2, y + int(h * 0.34)
    for r in range(40, 84, 7):
        d.ellipse([cx - r, cy - r, cx + r, cy + r],
                  outline=pal["photo_ring"], width=1)
    # faint lighthouse watermark, bottom right of the photo
    lx, ly = x + w - 26, y + h - 30
    d.polygon([(lx - 4, ly + 14), (lx - 2, ly - 8), (lx + 2, ly - 8),
               (lx + 4, ly + 14)], fill=pal["photo_ring"])
    d.ellipse([lx - 4, ly - 13, lx + 4, ly - 6], fill=pal["gold"])

    skin, skin_d, skin_l = pal["skin"], pal["skin_dark"], pal["skin_light"]
    hair, hair_d = pal["hair"], pal["hair_dark"]
    # shoulders / sweater with shading
    d.polygon([(x + 6, y + h), (x + w - 6, y + h),
               (x + w - 16, y + int(h * 0.64)),
               (x + w // 2 + 30, y + int(h * 0.60)),
               (x + w // 2 - 30, y + int(h * 0.60)),
               (x + 16, y + int(h * 0.64))], fill=pal["sweater"])
    d.polygon([(x + 6, y + h), (x + 26, y + int(h * 0.70)),
               (x + 22, y + int(h * 0.64)), (x + 16, y + int(h * 0.64))],
              fill=(28, 66, 62))
    d.polygon([(x + w - 6, y + h), (x + w - 26, y + int(h * 0.70)),
               (x + w - 22, y + int(h * 0.64)), (x + w - 16, y + int(h * 0.64))],
              fill=(28, 66, 62))
    # cream V collar
    d.polygon([(cx - 28, y + int(h * 0.60)), (cx + 28, y + int(h * 0.60)),
               (cx + 12, y + int(h * 0.72)), (cx - 12, y + int(h * 0.72))],
              fill=pal["paper"])
    d.polygon([(cx - 28, y + int(h * 0.60)), (cx + 28, y + int(h * 0.60)),
               (cx, y + int(h * 0.70))], fill=(226, 219, 200))
    # gold anchor pin on the left chest
    px, py = x + 34, y + int(h * 0.82)
    d.ellipse([px - 3, py - 8, px + 3, py - 2], outline=pal["gold"], width=2)
    d.line([(px, py - 2), (px, py + 8)], fill=pal["gold"], width=2)
    d.line([(px - 7, py + 2), (px + 7, py + 2)], fill=pal["gold"], width=2)
    d.polygon([(px - 7, py + 2), (px - 4, py + 9), (px - 1, py + 2)],
              fill=pal["gold"])
    d.polygon([(px + 7, py + 2), (px + 4, py + 9), (px + 1, py + 2)],
              fill=pal["gold"])
    # neck + shadow under the chin
    d.rectangle([cx - 12, y + int(h * 0.50), cx + 12, y + int(h * 0.62)],
                fill=skin_d)
    d.ellipse([cx - 14, y + int(h * 0.50), cx + 14, y + int(h * 0.58)],
              fill=(172, 122, 92))
    # face: oval with a narrower chin
    d.ellipse([cx - 33, y + int(h * 0.09), cx + 33, y + int(h * 0.52)],
              fill=skin)
    d.polygon([(cx - 30, y + int(h * 0.38)), (cx + 30, y + int(h * 0.38)),
               (cx + 16, y + int(h * 0.53)), (cx - 16, y + int(h * 0.53))],
              fill=skin)
    # cheek shading + light
    d.arc([cx - 33, y + int(h * 0.09), cx + 33, y + int(h * 0.52)],
          205, 335, fill=skin_d, width=2)
    d.ellipse([cx - 26, y + int(h * 0.16), cx - 8, y + int(h * 0.30)],
              fill=skin_l)
    # ears
    d.ellipse([cx - 38, y + int(h * 0.28), cx - 30, y + int(h * 0.40)],
              fill=skin)
    d.ellipse([cx + 30, y + int(h * 0.28), cx + 38, y + int(h * 0.40)],
              fill=skin)
    # hair: back mass, centre part, side strands, bun
    d.pieslice([cx - 38, y + int(h * 0.015), cx + 38, y + int(h * 0.44)],
               180, 360, fill=hair)
    d.polygon([(cx - 38, y + int(h * 0.18)), (cx - 28, y + int(h * 0.18)),
               (cx - 31, y + int(h * 0.50)), (cx - 40, y + int(h * 0.44))],
              fill=hair)
    d.polygon([(cx + 38, y + int(h * 0.18)), (cx + 28, y + int(h * 0.18)),
               (cx + 31, y + int(h * 0.50)), (cx + 40, y + int(h * 0.44))],
              fill=hair)
    # swept fringe: two masses meeting at a centre part
    d.polygon([(cx - 34, y + int(h * 0.10)), (cx - 2, y + int(h * 0.075)),
               (cx - 4, y + int(h * 0.16)), (cx - 30, y + int(h * 0.20))],
              fill=hair)
    d.polygon([(cx + 34, y + int(h * 0.10)), (cx + 2, y + int(h * 0.075)),
               (cx + 4, y + int(h * 0.16)), (cx + 30, y + int(h * 0.20))],
              fill=hair)
    d.ellipse([cx - 15, y + int(h * 0.015) - 9, cx + 15,
               y + int(h * 0.015) + 15], fill=hair)
    for dx in (-20, -8, 6, 18):
        d.line([(cx + dx, y + int(h * 0.09)), (cx + dx + 3, y + int(h * 0.20))],
               fill=hair_d, width=1)
    # brows: arched
    d.line([(cx - 25, y + int(h * 0.295)), (cx - 17, y + int(h * 0.275)),
            (cx - 9, y + int(h * 0.29))], fill=hair_d, width=2)
    d.line([(cx + 9, y + int(h * 0.29)), (cx + 17, y + int(h * 0.275)),
            (cx + 25, y + int(h * 0.295))], fill=hair_d, width=2)
    # eyes: white, iris, highlight
    for ex in (cx - 17, cx + 17):
        ey = y + int(h * 0.325)
        d.ellipse([ex - 8, ey - 4, ex + 8, ey + 4], fill=(250, 248, 244))
        d.ellipse([ex - 4, ey - 4, ex + 4, ey + 4], fill=(52, 44, 40))
        d.ellipse([ex - 1, ey - 3, ex + 2, ey], fill=(255, 255, 255))
        d.line([(ex - 8, ey - 5), (ex + 8, ey - 5)], fill=hair_d, width=1)
    # nose: soft shadow + base
    d.line([(cx - 1, y + int(h * 0.35)), (cx - 3, y + int(h * 0.425))],
           fill=skin_d, width=2)
    d.line([(cx - 4, y + int(h * 0.43)), (cx + 4, y + int(h * 0.43))],
           fill=skin_d, width=2)
    # lips: shaped, two-tone
    my = y + int(h * 0.465)
    d.polygon([(cx - 10, my), (cx - 4, my - 3), (cx, my - 1), (cx + 4, my - 3),
               (cx + 10, my), (cx, my + 2)], fill=pal["lip_dark"])
    d.polygon([(cx - 9, my + 1), (cx + 9, my + 1), (cx + 5, my + 6),
               (cx - 5, my + 6)], fill=pal["lip"])
    d.line([(cx - 5, my + 3), (cx + 5, my + 3)], fill=(196, 130, 118),
           width=1)
    d.rectangle([x, y, x + w, y + h], outline=pal["ink"], width=2)


def draw_fingerprint(d, box, ink):
    x, y, w, h = box
    cx, cy = x + w // 2, y + h // 2
    for r in range(6, max(w, h) // 2 + 4, 5):
        d.arc([cx - r, cy - r * 0.9, cx + r, cy + r * 0.9],
              200, 340 - r * 2, fill=ink, width=1)
    d.arc([cx - 14, cy - 12, cx + 14, cy + 12], 0, 360, fill=ink, width=1)


def draw_tide_curve(d, box, pal):
    """One day's tide at Port Lowick, 17 MAR 2024: LW 05:02 and
    17:26, causeway dry while the water is below deck level."""
    x, y, w, h = box
    ink = pal["ink"]
    d.rectangle([x, y, x + w, y + h], outline=ink, width=1)
    centred(d, x + w // 2, y + 6, "CAUSEWAY — ONE DAY'S TIDE · 17 MAR 2024",
            F_sansb(9), ink)
    ox, oy = x + 34, y + 30
    cw, ch = w - 48, h - 62
    # axes
    d.line([(ox, oy), (ox, oy + ch)], fill=ink, width=1)
    d.line([(ox, oy + ch), (ox + cw, oy + ch)], fill=ink, width=1)
    for hr, lab in ((0, "00"), (6, "06"), (12, "12"), (18, "18"),
                    (24, "24")):
        gx = ox + cw * hr / 24.0
        d.line([(gx, oy + ch), (gx, oy + ch + 4)], fill=ink, width=1)
        text(d, (gx, oy + ch + 6), lab, F_sans(8), ink, anchor="ma")
    text(d, (x + 8, oy + 2), "HW", F_sans(8), ink)
    text(d, (x + 8, oy + ch - 10), "LW", F_sans(8), ink)
    # causeway deck level (dry below this line): the deck sits just
    # above low water, so the water is below it only +/-45 min of LW
    deck = oy + ch * 0.11
    for gx in range(ox, ox + cw, 6):
        d.line([(gx, deck), (gx + 3, deck)], fill=pal["burgundy"], width=1)
    text(d, (ox + cw - 2, deck - 14), "CAUSEWAY DECK", F_sans(7),
         pal["burgundy"], anchor="ra")
    # tide curve: semidiurnal, HW ~23:00 / 11:00, LW 05:02 / 17:26
    pts = []
    for i in range(0, cw + 1, 3):
        hr = i / cw * 24.0
        lvl = 0.5 - 0.5 * math.cos(2 * math.pi * (hr - 5.03) / 12.4)
        pts.append((ox + i, oy + ch * 0.08 + ch * 0.84 * lvl))
    # shade the dry windows (water below deck)
    for (wx0, wx1, lab) in ((4.28, 5.78, "OPEN 04:17–05:47"),
                            (16.68, 18.18, "OPEN 16:41–18:11")):
        sx0 = ox + cw * wx0 / 24.0
        sx1 = ox + cw * wx1 / 24.0
        d.rectangle([sx0, deck, sx1, oy + ch], fill=pal["green"] + (36,))
        text(d, ((sx0 + sx1) / 2, oy + ch - 16), lab, F_sansb(7),
             pal["green"], anchor="ma")
    d.line(pts, fill=pal["accent"], width=2)
    for hr in (5.03, 17.43):
        gx = ox + cw * hr / 24.0
        gy = oy + ch * 0.08 + ch * 0.84 * (0.5 - 0.5 * math.cos(0))
        d.ellipse([gx - 3, gy - 3, gx + 3, gy + 3], fill=pal["burgundy"])
    text(d, (ox + cw * 5.03 / 24.0, oy + ch * 0.08 - 14), "LW 05:02",
         F_sansb(8), pal["burgundy"], anchor="ma")
    text(d, (ox + cw * 17.43 / 24.0, oy + ch * 0.08 - 14), "LW 17:26",
         F_sansb(8), pal["burgundy"], anchor="ma")


def render():
    pal = PAL
    img = Image.new("RGB", (W, H), pal["desk"])
    d = ImageDraw.Draw(img, "RGBA")
    ink, accent, gold = pal["ink"], pal["accent"], pal["gold"]

    LX, RX, TY, BY = 30, 524, 96, 928
    PW = 470
    d.rectangle([LX + 6, TY + 8, LX + PW + 6, BY + 8], fill=(0, 0, 0, 90))
    d.rectangle([RX + 6, TY + 8, RX + PW + 6, BY + 8], fill=(0, 0, 0, 90))
    d.rectangle([LX, TY, LX + PW, BY], fill=pal["page"])
    d.rectangle([RX, TY, RX + PW, BY], fill=pal["page"])
    d.rectangle([LX + PW - 4, TY, RX + 4, BY], fill=(0, 0, 0, 55))
    R.guilloche(d, (LX, TY, LX + PW, BY), pal["accent"], 13)
    R.guilloche(d, (RX, TY, RX + PW, BY), pal["accent"], 13)
    wm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wm)
    wd.ellipse([RX + 330, TY + 560, RX + 430, TY + 660],
               outline=pal["accent"] + (22,), width=2)
    wd.polygon([(RX + 378, TY + 600), (RX + 374, TY + 560),
                (RX + 382, TY + 560)], fill=pal["accent"] + (22,))
    img.paste(wm, (0, 0), wm)
    d = ImageDraw.Draw(img, "RGBA")
    frame(d, (LX, TY, LX + PW, BY), pal)
    frame(d, (RX, TY, RX + PW, BY), pal)

    # ================================================= LEFT PAGE: visas
    cx = LX + PW // 2
    centred(d, cx, TY + 18, "VISAS", F_head(27), ink)
    centred(d, cx, TY + 52, "VISA  ·  ENDORSEMENTS  ·  PORT LOWICK",
            F_sans(10), ink)
    rule(d, LX + 24, LX + PW - 24, TY + 72, gold, 2)
    rule(d, LX + 24, LX + PW - 24, TY + 76, ink, 1)

    R.draw_map(d, (LX + 24, TY + 90, 200, 148), pal)
    R.draw_tide_table(d, (LX + 236, TY + 90, 210, 148), pal)

    # two visas side by side
    R.stamp_rect(d, (LX + 24, TY + 254, 205, 92),
                 ["ALDERVIK — TIDEWAY VISA", "SINGLE ENTRY",
                  "ISSUED 05 MAR 2024", "VALID TO 04 APR 2024",
                  "REGISTER IN 1 DAY"],
                 pal["burgundy"], -1.5, size=10, gap=14)
    R.stamp_rect(d, (LX + 241, TY + 254, 205, 92),
                 ["KESSIG — HARBOUR VISA", "MULTIPLE ENTRY",
                  "ISSUED 02 JUN 2024", "VALID TO 30 JUN 2024",
                  "LEVY PAID · 12 CR"],
                 pal["green"], 1.5, size=10, gap=14)
    R.stamp_round(d, LX + 426, TY + 338, 24,
                  ["KESSIG", "09 JUN", "2024"], pal["green"], -10)

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
    sy = TY + 366
    for i, (lines, colour, ang) in enumerate(stamps):
        col = i % 2
        row = i // 2
        bx = LX + 24 + col * 213
        by = sy + row * 78
        lines = [ln for ln in lines if ln]
        R.stamp_rect(d, (bx, by, 205, 66), lines, colour, ang,
                     size=12, gap=14)

    R.stamp_round(d, LX + 78, TY + 724, 54,
                  ["FERRY LEVY", "12 CR", "PAID", "PORT LOWICK"],
                  pal["burgundy"], -8)
    ex = LX + 150
    ey = TY + 690
    text(d, (ex, ey), "ENDORSEMENT", F_sansb(11), ink)
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
        text(d, (ex, ey + 26 + j * 15), ln, F_serifi(12), ink)

    rule(d, LX + 24, LX + PW - 24, TY + 786, gold, 1)
    centred(d, cx, TY + 794,
            "PORT LOWICK · HARBOURMASTER'S OFFICE —",
            F_sansb(9), ink)
    centred(d, cx, TY + 808,
            "THE CAUSEWAY OPENS AT LOW WATER ONLY",
            F_sans(9), ink)
    text(d, (LX + 24, BY - 26), "4", F_sans(10), ink)

    # ================================================= RIGHT PAGE: data
    cx = RX + PW // 2
    centred(d, cx, TY + 18, "REPUBLIC OF TIDEMERE", F_head(29), ink)
    centred(d, cx, TY + 54, "P A S S P O R T", F_sansb(14), ink)
    centred(d, cx, TY + 74, "PASSEPORT", F_serifi(11), ink)
    R.coat_of_arms(d, cx, TY + 134, 50, ink, gold, accent)
    centred(d, cx, TY + 174, "·  THE TIDE PROVIDES  ·", F_serifi(12), ink)
    rule(d, RX + 24, RX + PW - 24, TY + 196, gold, 2)
    rule(d, RX + 24, RX + PW - 24, TY + 200, ink, 1)

    photo = (RX + 24, TY + 216, 150, 188)
    draw_portrait_v4(d, photo, pal)
    R.stamp_round(d, photo[0] + photo[2] - 20, photo[1] + photo[3] - 20,
                  26, ["PORT LOWICK", "02 FEB", "2024"], pal["burgundy"],
                  12)

    fx = RX + 190
    fy = TY + 216
    for label, val, dx in (("TYPE", "P", 0), ("CODE", "TDM", 74),
                           ("No.", "TDM 482 913", 148)):
        text(d, (fx + dx, fy), label, F_sans(9), accent)
        text(d, (fx + dx, fy + 13), val, F_serifb(15), ink)
    text(d, (fx, fy + 44), "NATIONALITY", F_sans(9), accent)
    text(d, (fx, fy + 57), "TIDEMERIAN", F_serifb(15), ink)
    text(d, (fx, fy + 88), "OCCUPATION", F_sans(9), accent)
    text(d, (fx, fy + 101), "TIDE PILOT", F_serifb(15), ink)
    text(d, (fx, fy + 132), "SEX", F_sans(9), accent)
    text(d, (fx, fy + 145), "F", F_serifb(15), ink)

    fields = [
        ("SURNAME", "VOSS", "GIVEN NAMES", "ELENA MARIS"),
        ("DATE OF BIRTH", "14 MAR 1988", "PLACE OF BIRTH", "PORT LOWICK"),
        ("DATE OF ISSUE", "02 FEB 2024", "DATE OF EXPIRY", "01 FEB 2034"),
        ("HEIGHT", "172 CM", "EYES", "GREY-GREEN"),
    ]
    gy = TY + 426
    for i, (l1, v1, l2, v2) in enumerate(fields):
        yy = gy + i * 52
        for label, val, xx in ((l1, v1, RX + 24), (l2, v2, RX + 256)):
            text(d, (xx, yy), label, F_sans(9), accent)
            text(d, (xx, yy + 13), val, F_serifb(16), ink)
        rule(d, RX + 24, RX + PW - 24, yy + 40, pal["photo_ring"], 1)

    ay = TY + 642
    text(d, (RX + 24, ay), "AUTHORITY", F_sans(9), accent)
    text(d, (RX + 24, ay + 13), "MINISTRY OF THE TIDE — PORT LOWICK",
         F_serifb(15), ink)
    sy = TY + 692
    text(d, (RX + 24, sy), "Elena Maris Voss", F_serifi(21), ink)
    rule(d, RX + 24, RX + 250, sy + 30, ink, 1)
    text(d, (RX + 24, sy + 36), "HOLDER'S SIGNATURE", F_sans(9), accent)
    draw_fingerprint(d, (RX + 336, TY + 668, 58, 58), ink)
    centred(d, RX + 365, TY + 730, "RIGHT INDEX", F_sans(8), ink)

    mz = (RX + 24, TY + 750, RX + 24 + 422, TY + 750 + 56)
    d.rectangle(mz, fill=(255, 255, 255, 110), outline=ink, width=1)
    l1, l2 = R.mrz_lines()
    text(d, (mz[0] + 10, mz[1] + 7), l1, F_mono(15), ink)
    text(d, (mz[0] + 10, mz[1] + 30), l2, F_mono(15), ink)
    centred(d, cx, BY - 26,
            "THIS PASSPORT IS THE PROPERTY OF THE REPUBLIC OF TIDEMERE",
            F_sans(8), ink)
    text(d, (RX + PW - 24, BY - 26), "5", F_sans(10), ink, anchor="ra")

    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "variant-v4.png"
    img = render()
    img.save(out, "PNG", optimize=True)
    size = os.path.getsize(out)
    print(f"v4: wrote {out} {img.size[0]}x{img.size[1]} {size} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
