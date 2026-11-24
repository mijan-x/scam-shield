"""Lightweight checks on the screenshot file itself (no AI needed).

- Editing-app traces in the file metadata (EXIF / PNG text chunks).
- Image size sanity.
- A perceptual fingerprint (difference hash), so the same screenshot sent for two
  different orders is caught even after re-saving or slight resizing.

These are clues, not proof: editing apps can strip metadata, and a clean file can
still be fake. The UI says so.
"""
import io
import re

from PIL import Image, ImageOps

EDITORS = re.compile(
    r"photoshop|lightroom|gimp|snapseed|picsart|canva|pixlr|meitu|polarr|facetune|photopea|"
    r"affinity|paint\.net|photo ?editor|photodirector|vsco|remini|inshot|ibis|"
    # phone gallery editors (Samsung, Google, Apple, Xiaomi, Oppo/Realme, Vivo, Huawei)
    r"samsung photo|galaxy enhance|google photos|apple photos|markup|miui gallery|mi gallery|"
    r"coloros|realme gallery|vivo gallery|huawei gallery|photo ?studio|photoroom|lightx|polish",
    re.I,
)
# editing apps also leave their names in XMP or other blocks inside the file
RAW_EDITORS = re.compile(
    rb"Photoshop|Lightroom|Snapseed|PicsArt|Canva|Pixlr|Meitu|Polarr|Photopea|PhotoDirector|"
    rb"Samsung Photo Editor|Photo Editor|Google Photos|Markup|MIUI Gallery|photoshop:History|"
    rb"xmpMM:History|stEvt:action=\"(?:saved|derived)\"",
    re.I,
)


def fingerprint(img: Image.Image) -> int:
    """64-bit difference hash."""
    g = ImageOps.exif_transpose(img).convert("L").resize((9, 8), Image.LANCZOS)
    px = list(g.tobytes())
    bits = 0
    for row in range(8):
        for col in range(8):
            bits = (bits << 1) | (px[row * 9 + col] > px[row * 9 + col + 1])
    return bits


def hamming(a: int, b: int) -> int:
    return bin(a ^ b).count("1")


def inspect(data: bytes) -> dict:
    """Raises ValueError if the bytes are not a readable image."""
    try:
        img = Image.open(io.BytesIO(data))
        img.load()
    except Exception as e:  # noqa: BLE001
        raise ValueError("not a readable image") from e

    software = []
    try:
        exif = img.getexif()
        for tag in (0x0131, 0x013B, 0x010F):  # Software, Artist, Make
            v = exif.get(tag)
            if v:
                software.append(str(v))
    except Exception:  # noqa: BLE001
        pass
    for k, v in (img.info or {}).items():
        if isinstance(v, str) and k.lower() in ("software", "comment", "description", "creator", "xml:com.adobe.xmp"):
            software.append(v[:300])
    editor = None
    for s in software:
        m = EDITORS.search(s)
        if m:
            editor = m.group(0)
            break
    if not editor:
        m = RAW_EDITORS.search(data[:300000])
        if m:
            editor = m.group(0).decode("latin-1")[:40]
            editor = "editing history" if editor.lower().startswith(("xmpmm", "stevt", "photoshop:history")) else editor

    # a file saved again after it was made: the 'modified' time is later than the 'taken' time
    modified_after = None
    try:
        exif = img.getexif()
        changed = exif.get(0x0132)  # DateTime (last saved)
        original = exif.get_ifd(0x8769).get(0x9003) or exif.get_ifd(0x8769).get(0x9004)  # DateTimeOriginal / Digitized
        if changed and original and str(changed).strip() != str(original).strip():
            from datetime import datetime as _dt
            a = _dt.strptime(str(original).strip()[:19], "%Y:%m:%d %H:%M:%S")
            b = _dt.strptime(str(changed).strip()[:19], "%Y:%m:%d %H:%M:%S")
            if (b - a).total_seconds() > 60:
                modified_after = int((b - a).total_seconds() // 60)
    except Exception:  # noqa: BLE001
        pass

    w, h = img.size
    return {
        "format": img.format,
        "width": w,
        "height": h,
        "editor": editor,
        "modified_after_min": modified_after,
        "software": "; ".join(software)[:200] or None,
        "hash": fingerprint(img),
    }


def zoom_strip(data: bytes, boxes: dict, order=("amount", "trx_id", "datetime", "recipient", "sender", "label")):
    """Cut each field out of the screenshot, enlarge it and stack the pieces into one labelled image.

    boxes: field -> [ymin, xmin, ymax, xmax] on a 0-1000 scale. Returns PNG bytes, or None."""
    from PIL import ImageDraw
    img = ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert("RGB")
    W, H = img.size
    rows = []
    for f in order:
        b = boxes.get(f) if isinstance(boxes, dict) else None
        if not (isinstance(b, list) and len(b) == 4 and all(isinstance(v, (int, float)) for v in b)):
            continue
        y0, x0, y1, x1 = [max(0.0, min(1000.0, float(v))) / 1000 for v in b]
        if y1 <= y0 or x1 <= x0:
            continue
        ph, pw = (y1 - y0) * 0.35, (x1 - x0) * 0.08
        box = (int(max(0, x0 - pw) * W), int(max(0, y0 - ph) * H), int(min(1, x1 + pw) * W), int(min(1, y1 + ph) * H))
        if box[2] - box[0] < 4 or box[3] - box[1] < 4:
            continue
        crop = img.crop(box)
        k = min(120 / crop.height, 1100 / crop.width, 6.0)
        rows.append((f, crop.resize((max(1, int(crop.width * k)), max(1, int(crop.height * k))), Image.LANCZOS)))
    if len(rows) < 2:
        return None
    label_w = 130
    width = label_w + max(r.width for _, r in rows) + 20
    height = sum(r.height + 16 for _, r in rows) + 8
    out = Image.new("RGB", (width, height), "white")
    d = ImageDraw.Draw(out)
    try:
        from PIL import ImageFont
        font = ImageFont.load_default(size=20)
    except Exception:  # noqa: BLE001  (older Pillow)
        font = None
    y = 8
    for name, r in rows:
        d.text((8, y + r.height // 2 - 10), name, fill=(200, 0, 0), font=font)
        out.paste(r, (label_w, y))
        d.rectangle([label_w - 1, y - 1, label_w + r.width, y + r.height], outline=(180, 180, 180))
        y += r.height + 16
    buf = io.BytesIO()
    out.save(buf, "PNG")
    return buf.getvalue()
