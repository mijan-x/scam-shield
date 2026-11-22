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
    r"affinity|paint\.net|photo editor|photodirector|vsco|remini|picsart|inshot|ibis",
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

    w, h = img.size
    return {
        "format": img.format,
        "width": w,
        "height": h,
        "editor": editor,
        "software": "; ".join(software)[:200] or None,
        "hash": fingerprint(img),
    }
