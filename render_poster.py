#!/usr/bin/env python3
"""Render entry.png (1024x1024) — the "World in One Day" front page.

Implements the design in poster.html (same content, palette and structure)
with Pillow and the system Noto Serif faces, because this machine's Chromium
build cannot run headless screenshots. The layout is flow-based with an
auto-fit pass: type sizes scale down in fixed steps until the whole page
fits the canvas, so the result is deterministic — same bytes every run.

Usage: python3 render_poster.py [output-path]   (default: ./entry.png)
"""
import sys
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MX = 36                      # side margin
CW = W - 2 * MX              # content width = 952

PAPER = (247, 243, 234)
INK = (22, 19, 14)
BODY = (38, 34, 27)
GRAY = (76, 70, 60)
RED = (155, 28, 28)
TINT = (239, 232, 216)
HAIR = (201, 194, 178)

SERIF_B = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
SERIF_R = "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf"

LEAD_TEXT = ("The leaders of the United States, China and Russia held a landmark "
             "trilateral summit in Shenzhen, the first meeting of its kind, "
             "overshadowing the APEC gathering and raising hopes and fears over "
             "trade and the war in Ukraine.")
BAND_TEXT = ("Kyiv says its naval drones destroyed the corvette Mercury in Benghazi "
             "harbour, over 1,000 miles from home. Overnight, Russian drone strikes "
             "on the Kyiv region killed 11 people, and a Russian drone entered Polish "
             "airspace, putting Poland’s air defence on alert.")
CELLS = [
    ("BUSINESS · TECHNOLOGY", "Nvidia reinstates CEO Jensen Huang",
     "Nvidia’s board restored Huang as chief executive 11 days after he resigned, "
     "following intervention by President Trump. Washington blacklisted Singapore "
     "chip firm Megaspeed over alleged smuggling, and Nvidia shares surged."),
    ("MIDDLE EAST", "Tensions flare between Iran and the United States",
     "Iran’s Revolutionary Guard said three tankers struck sea mines in the Strait "
     "of Hormuz. The US sanctioned Iranian money-exchange networks, and Trump "
     "warned of a ‘very traumatic’ outcome if nuclear talks fail."),
    ("ASIA", "Russian jets trigger shelter alert in South Korea",
     "Russian warplanes entered South Korea’s air defence zone without notice; "
     "residents of Ulleung Island were told to take shelter as Seoul scrambled jets."),
    ("CLIMATE", "COP31 climate talks under way in Antalya",
     "World leaders in Türkiye are debating climate finance and fossil fuel "
     "commitments, with deep divisions between rich and developing nations."),
]
BRIEFS_L = [
    "Mexico arrests cartel leader ‘El Chapo Isidro’ and says it will try him at "
    "home, defying a US extradition request.",
    "Bangladesh begins a campaign to vaccinate 50 million children against "
    "drug-resistant typhoid.",
    "Trump will meet NATO chief Mark Rutte in Florida on Wednesday, the White "
    "House says.",
]
BRIEFS_R = [
    "A world court ruling finds Myanmar committed genocide against the Rohingya.",
    "FIFA confirms the 2031 Women’s World Cup for the US, Mexico, Costa Rica and "
    "Jamaica, and the 2035 edition for the UK.",
    "Cambridge Dictionary names ‘human’ its Word of the Year for 2026.",
]


def render(scale):
    def S(v):
        return max(8, round(v * scale))

    def F(path, size):
        return ImageFont.truetype(path, S(size))

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    def tw(s, font, tracking=0):
        return sum(d.textlength(ch, font=font) for ch in s) + tracking * max(0, len(s) - 1)

    def tracked(x, y, s, font, fill, tracking=0, center=False):
        if center:
            x = MX + (CW - tw(s, font, tracking)) / 2
        cx = x
        for ch in s:
            d.text((cx, y), ch, font=font, fill=fill)
            cx += d.textlength(ch, font=font) + tracking

    def wrap(text, font, max_w):
        lines, cur = [], ""
        for word in text.split():
            trial = (cur + " " + word).strip()
            if d.textlength(trial, font=font) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def para(x, y, text, font, lh, fill, max_w):
        for line in wrap(text, font, max_w):
            d.text((x, y), line, font=font, fill=fill)
            y += lh
        return y

    def rule(y, weight=2, fill=INK):
        d.rectangle([MX, y, W - MX, y + weight - 1], fill=fill)
        return y + weight

    def double_rule(y):
        rule(y, 3)
        rule(y + 5, 1)
        return y + 6

    kf = F(SERIF_B, 13)
    sf = F(SERIF_R, 16)
    y = S(26)

    # ---------------- Masthead ----------------
    over = "ONE IMAGE · THE DAY’S WORLD NEWS"
    of = F(SERIF_B, 14)
    ow = tw(over, of, S(4))
    ox = MX + (CW - ow) / 2
    d.line([MX, y + S(8), ox - 16, y + S(8)], fill=INK, width=1)
    d.line([ox + ow + 16, y + S(8), W - MX, y + S(8)], fill=INK, width=1)
    tracked(MX, y, over, of, GRAY, S(4), center=True)
    y += S(26)

    tf = F(SERIF_B, 64)
    title = "THE WORLD IN ONE DAY"
    d.text((MX + (CW - d.textlength(title, font=tf)) / 2, y), title, font=tf, fill=INK)
    y += S(78)

    df = F(SERIF_B, 33)
    date = "Tuesday 24 November 2026"
    d.rectangle([MX, y, W - MX, y + S(54)], fill=RED)
    tracked(MX, y + S(8), date, df, PAPER, S(2), center=True)
    y += S(62)
    y = double_rule(y) + S(14)

    # ---------------- Lead story ----------------
    tracked(MX, y, "THE LEAD · SHENZHEN, CHINA", kf, RED, S(3))
    y += S(22)
    lf = F(SERIF_B, 50)
    y = para(MX, y, "Trump, Xi and Putin meet in Shenzhen", lf, S(56), INK, CW)
    bf = F(SERIF_R, 18)
    y = para(MX, y + S(6), LEAD_TEXT, bf, S(26), BODY, CW)
    y += S(12)
    y = rule(y, 3) + S(13)

    # ---------------- Band story ----------------
    tracked(MX, y, "UKRAINE · LIBYA · POLAND", kf, RED, S(3))
    y += S(22)
    hf = F(SERIF_B, 29)
    y = para(MX, y, "Ukraine says sea drones sank a Russian warship in Libya", hf, S(34), INK, CW)
    y = para(MX, y + S(5), BAND_TEXT, sf, S(23), BODY, CW)
    y += S(11)
    y = rule(y, 2) + S(13)

    # ---------------- Grid: stories 3-6 ----------------
    COLW = 458
    X1, X2 = MX, W - MX - COLW
    gf = F(SERIF_B, 26)
    kf2 = F(SERIF_B, 12)

    def cell(x, y, kicker, head, text):
        tx = x + 13
        head_lines = wrap(head, gf, COLW - 13)
        body_lines = wrap(text, sf, COLW - 13)
        cell_h = S(19) + len(head_lines) * S(31) + S(4) + len(body_lines) * S(23)
        d.rectangle([x, y + 2, x + 2, y + cell_h - 4], fill=RED)
        tracked(tx, y, kicker, kf2, RED, S(2))
        yy = y + S(19)
        for line in head_lines:
            d.text((tx, yy), line, font=gf, fill=INK)
            yy += S(31)
        yy += S(4)
        for line in body_lines:
            d.text((tx, yy), line, font=sf, fill=BODY)
            yy += S(23)
        return yy

    grid_top = y
    left_end = cell(X1, grid_top, *CELLS[0])
    right_end = cell(X2, grid_top, *CELLS[1])
    row2 = max(left_end, right_end) + S(14)
    d.line([X1, row2 - S(8), X1 + COLW, row2 - S(8)], fill=HAIR, width=1)
    d.line([X2, row2 - S(8), X2 + COLW, row2 - S(8)], fill=HAIR, width=1)
    left_end = cell(X1, row2, *CELLS[2])
    right_end = cell(X2, row2, *CELLS[3])
    y = max(left_end, right_end) + S(11)
    y = rule(y, 2) + S(12)

    # ---------------- Briefs ----------------
    pf = F(SERIF_R, 15)
    BCOLW = (CW - 28 - 28) // 2

    def brief_h(text):
        return len(wrap(text, pf, BCOLW - 16)) * S(21)

    col_l = sum(brief_h(b) for b in BRIEFS_L) + S(7) * (len(BRIEFS_L) - 1)
    col_r = sum(brief_h(b) for b in BRIEFS_R) + S(7) * (len(BRIEFS_R) - 1)
    band_h = S(10) + S(32) + max(col_l, col_r) + S(10)
    d.rectangle([MX, y, W - MX, y + band_h], fill=TINT)
    bx = MX + 14
    by = y + S(10)
    hf2 = F(SERIF_B, 20)
    d.text((bx, by), "ALSO ON ", font=hf2, fill=INK)
    d.text((bx + d.textlength("ALSO ON ", font=hf2), by), "TUESDAY", font=hf2, fill=RED)
    by += S(32)

    def brief(x, y, text):
        for i, line in enumerate(wrap(text, pf, BCOLW - 16)):
            if i == 0:
                d.text((x + 2, y), "•", font=pf, fill=RED)
            d.text((x + 16, y), line, font=pf, fill=BODY)
            y += S(21)
        return y

    ly, ry = by, by
    for b in BRIEFS_L:
        ly = brief(bx, ly, b) + S(7)
    for b in BRIEFS_R:
        ry = brief(bx + BCOLW + 28, ry, b) + S(7)
    y += band_h + S(12)
    y = rule(y, 3) + S(10)

    # ---------------- Footer ----------------
    y = double_rule(y) + S(9)
    ff = F(SERIF_R, 13)
    d.text((MX, y), "Compiled from the day’s reporting: Reuters · The Guardian · "
                    "BBC · Al Jazeera · Deutsche Welle", font=ff, fill=GRAY)
    fdf = F(SERIF_B, 13)
    d.text((W - MX - d.textlength(date, font=fdf), y), date, font=fdf, fill=RED)
    y += S(20)
    return img, y


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    for scale in (1.0, 0.96, 0.92, 0.88, 0.84, 0.80):
        img, bottom = render(scale)
        if bottom <= H - 8:
            break
    print(f"scale {scale}: content bottom {bottom} of {H}")
    img.save(out, format="PNG", optimize=True)


if __name__ == "__main__":
    main()
