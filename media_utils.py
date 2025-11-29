from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from config import UPLOAD_DIR


def add_brand_overlay(local_path: str) -> str:
    """
    Adds a simple brand text overlay to the bottom-right corner.
    Returns the new branded file path (relative: 'uploads/..').
    """
    src = Path(local_path)
    if not src.is_file():
        raise FileNotFoundError(f"Media not found: {src}")

    # Avoid double _branded.png
    if src.stem.endswith("_branded"):
        return str(src)

    branded_name = f"{src.stem}_branded{src.suffix}"
    branded_path = src.with_name(branded_name)

    img = Image.open(src).convert("RGBA")
    w, h = img.size

    overlay = Image.new("RGBA", img.size)
    draw = ImageDraw.Draw(overlay)

    text = "Jeng Frames"
    font_size = max(24, w // 30)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    tw, th = draw.textsize(text, font=font)
    margin = 20
    x = w - tw - margin
    y = h - th - margin

    draw.text((x, y), text, font=font, fill=(255, 255, 255, 200))

    combined = Image.alpha_composite(img, overlay)
    combined.convert("RGB").save(branded_path)

    # Return path relative to project root, using forward slashes
    rel = branded_path.relative_to(UPLOAD_DIR.parent).as_posix()
    return rel
