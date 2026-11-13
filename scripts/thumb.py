"""Thumbnail text by code (never by the image generator), 1280 x 720, yellow Impact capitals with a thick black outline.

  python thumb.py scene.jpg thumbnail.jpg "DO WOMEN REALLY|PREFER TALL MEN?" --fit        ("|" = line break)
  python thumb.py --selftest

  --fit[=0.7]  the scene is reduced to 70 % of the frame (letters about 90 px; 0.8 gave 58 px, half the size of the channel's best thumbnail, 11 Nov 2026) and pushed to the bottom, on a blurred, darkened copy of itself; the text
               sits in the free strip above it, so it can never cover a face (Flow fills the top of the frame with heads whatever the
               prompt says: thumb-blackmen-safe, 11 Nov 2026). A smaller value (0.7) gives a taller strip and bigger letters.
  --noband     without --fit: the text straight on the image (the scene must keep its top third empty)
  (default)    without --fit: a dark navy band across the top
  --force      skips the text lint

The text is the question of the title on two lines: the winning thumbnail of the channel (9.3 % of clicks, Studio 11 Nov 2026).
Lint: a question of 3 to 8 words, no word the ad classifier reads as sexual, no duration-like number.
This lint only catches known patterns: read the picture you made.
"""
import os, re, sys
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont

W, H = 1280, 720
YELLOW, NAVY = (242, 196, 70), (26, 40, 78)
FONT = "C:/Windows/Fonts/impact.ttf"
RISK = r"\b(sex|sexual|sexy|rape[ds]?|raping|porn\w*|orgasm\w*|nude[s]?|naked|fetish\w*|erotic\w*|nsfw|xxx|horny|adult content|genital\w*|masturbat\w*)\b"   # same list as yt/ypp_lint.py

def lint(text):
    t, words = text.upper().replace("|", " ").strip(), text.replace("|", " ").split()
    errors = []
    if not 3 <= len(words) <= 8: errors.append(f"{len(words)} words, 3 to 8 expected (the question of the title)")
    if not t.endswith("?"): errors.append("the text is the question of the title: it ends with \"?\"")
    if re.search(r"\b\d{1,2}:\d{2}\b", t): errors.append("duration-like number (3:47) looks like YouTube's timer")
    if m := re.search(RISK, t, flags=re.I): errors.append(f"ad-unfriendly word \"{m.group(0)}\"")
    return errors

def fit_font(d, lines, max_w, max_h, start):
    """Largest Impact size whose lines fit max_w wide and max_h high in all."""
    size = start
    while size > 20:
        f = ImageFont.truetype(FONT, size)
        if max(d.textlength(l, font=f) for l in lines) <= max_w and len(lines) * size * 1.12 <= max_h: return f
        size -= 2
    return ImageFont.truetype(FONT, 20)

def soft_mask(sw, sh, f=40):
    """White with a soft ramp on the top and side edges (the bottom touches the frame): no hard box around the reduced scene."""
    col = Image.new("L", (sw, 1)); col.putdata([min(255, 255 * min(k, sw - 1 - k) // f) for k in range(sw)])
    row = Image.new("L", (1, sh)); row.putdata([min(255, 255 * k // f) for k in range(sh)])
    return ImageChops.darker(col.resize((sw, sh)), row.resize((sw, sh)))

def compose(src, text, fit=None, noband=False):
    im = Image.open(src).convert("RGB"); lines = [l.strip() for l in text.split("|")] if text else []
    if fit:
        bg = ImageEnhance.Brightness(im.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(24))).enhance(0.5)
        sw, sh = round(W * fit), round(H * fit)
        bg.paste(im.resize((sw, sh), Image.LANCZOS), ((W - sw) // 2, H - sh), soft_mask(sw, sh)); im, band = bg, H - sh
    else:
        im = im.resize((W, H), Image.LANCZOS); band = 200 if len(lines) <= 1 else 300
    d = ImageDraw.Draw(im); size = 0
    if lines:
        if not fit and not noband: d.rectangle([0, 0, W, band], fill=NAVY)
        f = fit_font(d, lines, W - 80, band - 12, 150); size = f.size
        for n, l in enumerate(lines):
            d.text((W // 2, band * (2 * n + 1) // (2 * len(lines))), l, font=f, fill=YELLOW, anchor="mm", stroke_width=max(4, f.size // 13), stroke_fill=(0, 0, 0))
    return im, band, size

def selftest():
    assert lint("DO WOMEN REALLY|PREFER TALL MEN?") == []
    assert len(lint("TALL MEN")) == 2 and "ad-unfriendly" in lint("IS SEX REALLY BETTER?")[0] and "timer" in lint("WHY DO MEN WAKE AT 3:47?")[0]
    src = Image.new("RGB", (1376, 768), (200, 30, 30)); src.save("_thumb_selftest.png")
    im, band, size = compose("_thumb_selftest.png", "DO WOMEN REALLY|PREFER TALL MEN?", fit=0.8); os.remove("_thumb_selftest.png")
    assert im.size == (W, H) and band == 144 and size >= 50
    red = lambda p: p[0] > 150 and p[1] < 80
    assert all(red(im.getpixel((x, y))) for x in range(128 + 48, 1152 - 48, 16) for y in range(band + 48, H, 16)), "text or background over the scene"
    assert any(im.getpixel((x, y))[1] > 150 for x in range(300, 980, 4) for y in range(10, band - 10, 4)), "no yellow text in the strip"
    assert not any(im.getpixel((x, y))[1] > 150 for x in range(0, W, 4) for y in range(band + 8, H, 4)), "yellow text below the strip"
    print("selftest ok")

if __name__ == "__main__":
    if "--selftest" in sys.argv: selftest(); sys.exit(0)
    flags = [a for a in sys.argv[1:] if a.startswith("--")]
    src, dst, text = [a for a in sys.argv[1:] if not a.startswith("--")][:3]
    fit = next((float(a.split("=", 1)[1]) if "=" in a else 0.7 for a in flags if a.startswith("--fit")), None)
    if fit is not None and not 0.5 <= fit <= 0.9: sys.exit("--fit: between 0.5 and 0.9")
    if text and "--force" not in flags and (errs := lint(text)): sys.exit("thumbnail text refused: " + "; ".join(errs))
    im, band, size = compose(src, text, fit, "--noband" in flags)
    im.save(dst, quality=92, optimize=True)
    print(dst, im.size, f"{os.path.getsize(dst) / 1e6:.2f} MB" + (f" | scene at {fit:.0%}, text strip {band} px, letters {size} px" if fit else f" | letters {size} px"))
