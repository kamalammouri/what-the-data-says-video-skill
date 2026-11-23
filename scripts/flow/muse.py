"""Meta Muse (muse.ai), the backup image source when Google Flow refuses ("unusual activity") or is slow.

  python scripts/flow/muse.py batches prompts.json flow/<video> [--only F001,F009] [--out muse_batches.md]
      -> muse_batches.md: one chat message per batch of up to 4 images that need the same cast references (Muse makes 4 images
         a request at most), the shared style written once, then each image under its code; the files to attach are named.
         Images already in flow/<video> are skipped, so the command lists only what is left to make.
  python scripts/flow/muse.py import flow/<video> [--from ~/Downloads] [--order F001,F009,...] [--since 20] [--force]
      -> copies the images downloaded from Muse (media-generation-*.webp|png|jpg) into flow/<video>/F###.png. A file whose name
         holds its code (F012) goes to that code; the others (downloaded in the last --since minutes only) are taken oldest first and given the codes of --order. Muse puts the code in the name when the message asks for it (media-generation-f001-0-<id>.webp, 23 Nov 2026).
  python scripts/flow/muse.py --selftest

Measured on 22 Nov 2026 (free plan, Muse Spark 1.3, 4 scenes of medieval-bath-en): 4 images in about 1 min, all 2048x1152
(true 16:9) WebP, no text, the hero recognisable; the old reference.png (caveman with a spear) put a spear in a medieval street,
so the cast is attached as assets/cast/cast-sheet.png (23 Nov) and every message forbids weapons and bare legs. Download names are
Muse's own slugs (media-generation-hero-auberge-medievale-0-<id>.webp): download in the order of the batch, or ask Muse to put
the code in the file name. A page script cannot POST the files to 127.0.0.1 (muse.ai blocks it): use the Download button of the
image viewer. Muse Video (10 s, 1248x704, sound) lost the hero's design after 2 s: not for the cast (references/images-flow.md §3b).
"""
import json, os, pathlib, re, shutil, sys

CAST = pathlib.Path(__file__).resolve().parents[2] / "assets" / "cast"
MUSE_REF = {"reference.png": "hero-modern.png"}        # the caveman reference carries a spear and a fur: never sent to Muse
SHEET = "cast-sheet.png"   # hero (left), heroine (middle), friend (right) cut from Flow images without weapons (23 Nov 2026): sent for any cast
RULES = ("Rules for every image: landscape 16:9, 2048x1152. Keep only the design of the characters from the attached images "
         "(round white head, black dot eyes, hair, mustache, thin white stick body); ignore their clothes, props and background. "
         "No weapon, no spear, no stick in anyone's hand; legs covered by clothes unless the character is in water. "
         "No text, no letters, no speech bubble, no logo, no watermark. Other people are small plain stick figures, fully clothed.")
CODE = re.compile(r"(?<![A-Za-z0-9])(F\d{3})(?![0-9])", re.I)

NAMES = {"reference.png": "the hero (left of the sheet)", "heroine.png": "the heroine (middle)", "second-male.png": "the friend (right)"}
def refs_of(p): return (SHEET,) if p.get("refs") else ()
def who(items): return sorted({NAMES.get(r, r) for p in items for r in (p.get("refs") or [])})

def batches(prompts, size=4):
    """Groups prompts that need the same reference images, in shot order, `size` at most per group."""
    groups, order = {}, []
    for p in prompts:
        k = refs_of(p)
        if k not in groups: groups[k] = []; order.append(k)
        groups[k].append(p)
    out = []
    for k in order:
        g = groups[k]
        out += [(k, g[n:n + size]) for n in range(0, len(g), size)]
    return out

def message(refs, items):
    common = os.path.commonprefix([p["prompt"] for p in items]) if len(items) > 1 else ""
    common = common[:common.rfind(". ") + 1] if ". " in common else ""        # cut at a sentence end
    head = (f"Generate {len(items)} distinct images now with Muse Image. " + RULES
            + (f" The attached sheet shows the recurring cast: the hero on the left, the heroine in the middle, the friend on the right; these images use {', '.join(who(items))}." if refs else " No recurring character in these.")
            + " Name each file with its code (for example F012) and give me its size in pixels. Do not publish anything, do not connect any app.")
    rest = {p["file"]: [s.strip() for s in re.split(r"(?<=\.)\s+", p["prompt"][len(common):]) if s.strip()] for p in items}
    shared = [s for s in rest[items[0]["file"]] if len(items) > 1 and all(s in v for v in rest.values())]   # said once, not 4 times
    body = (f"\n\nShared style: {' '.join([common.strip()] + shared).strip()}" if common or shared else "")
    for p in items: body += f"\n\n{p['file']}: {' '.join(s for s in rest[p['file']] if s not in shared)}"
    return head + body

def cmd_batches(a):
    prompts = json.load(open(a[0], encoding="utf-8")); flow = pathlib.Path(a[1]) if len(a) > 1 and not a[1].startswith("--") else None
    only = set(a[a.index("--only") + 1].split(",")) if "--only" in a else None
    out = pathlib.Path(a[a.index("--out") + 1]) if "--out" in a else pathlib.Path("muse_batches.md")
    have = lambda f: flow and any((flow / f"{f}{e}").exists() for e in (".png", ".jpg", ".webp"))
    todo = [p for p in prompts if (not only or p["file"] in only) and not have(p["file"])]
    bs = batches(todo); lines = [f"# Muse batches: {len(todo)} images in {len(bs)} messages\n",
        "One message per batch: attach the files listed (from the skill's assets/cast/), paste the text, send, then open each image "
        "and press Download in the order of the codes. Then: python scripts/flow/muse.py import flow/<video> --order <the codes>.\n"]
    for n, (refs, items) in enumerate(bs, 1):
        lines.append(f"## Batch {n}: {', '.join(p['file'] for p in items)}  |  attach: {', '.join(refs) or 'nothing'}\n\n```\n{message(refs, items)}\n```\n")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"{out}: {len(todo)} images in {len(bs)} messages (4 at most each)" + (f", {len(prompts) - len(todo)} already in {flow}" if flow else ""))

def cmd_import(a):
    from PIL import Image
    flow = pathlib.Path(a[0]); flow.mkdir(parents=True, exist_ok=True)
    src = pathlib.Path(os.path.expanduser(a[a.index("--from") + 1] if "--from" in a else "~/Downloads"))
    order = [c.strip().upper() for c in a[a.index("--order") + 1].split(",")] if "--order" in a else []
    files = sorted((f for f in src.glob("media-generation-*") if f.suffix.lower() in (".webp", ".png", ".jpg", ".jpeg") and " (" not in f.name),
                   key=lambda f: f.stat().st_mtime)
    named = {f: m.group(1).upper() for f in files if (m := CODE.search(f.name))}
    import time
    fresh = time.time() - 60 * float(a[a.index("--since") + 1] if "--since" in a else 20)   # files without a code: only the last 20 minutes
    rest = [f for f in files if f not in named and f.stat().st_mtime >= fresh][-len(order):] if order else []
    pairs = list(named.items()) + list(zip(rest, [c for c in order if c not in named.values()]))
    done = []
    for f, code in pairs:
        dst = flow / f"{code}.png"
        if dst.exists() and "--force" not in a: continue
        Image.open(f).convert("RGB").save(dst); done.append(f"{code} <- {f.name}")
    print("\n".join(done) or "nothing new"); print(f"{len(done)} imported into {flow}" + ("" if pairs else " (no file with a code in its name: pass --order F001,F009,... in download order)"))

def selftest():
    ps = [{"file": f"F{n:03d}", "prompt": f"Bold 2D cartoon. Same style. Scene {n}.", "refs": r} for n, r in
          [(1, ["reference.png"]), (2, None), (3, ["reference.png"]), (4, ["reference.png"]), (5, ["reference.png"]), (6, ["reference.png"])]]
    b = batches(ps)
    assert [([p["file"] for p in it], k) for k, it in b] == [(["F001", "F003", "F004", "F005"], ("cast-sheet.png",)), (["F006"], ("cast-sheet.png",)), (["F002"], ())], b
    m = message(*b[0])
    assert "Shared style: Bold 2D cartoon. Same style." in m and "F003: Scene 3." in m and "No weapon" in m and "Do not publish" in m, m
    assert CODE.search("media-generation-F012-rue-0-ab.webp").group(1) == "F012" and not CODE.search("media-generation-hero-0-aa8d4365.webp")
    print("muse selftest ok")

if __name__ == "__main__":
    a = sys.argv[1:]
    if "--selftest" in a: selftest()
    elif a and a[0] == "batches": cmd_batches(a[1:])
    elif a and a[0] == "import": cmd_import(a[1:])
    else: print(__doc__)
