from __future__ import annotations
from typing import Optional, Tuple
from PIL import Image, ImageOps
import io

def _hex_to_rgb(hexcolor: str) -> tuple[int, int, int]:
    if not hexcolor:
        return (255, 255, 255)
    s = hexcolor.strip().lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    if len(s) != 6:
        raise ValueError("Invalid hex color (expected like #ffffff or #fff)")
    return tuple(int(s[i:i+2], 16) for i in (0, 2, 4))

def convert_image_bytes(
    *,
    data: bytes,
    width: Optional[int],
    height: Optional[int],
    fit: str,
    fmt: str,
    quality: int,
    background: Optional[str],
) -> Tuple[bytes, str]:
    # Ouvrir l'image
    try:
        im = Image.open(io.BytesIO(data))
    except Exception:
        raise ValueError("Unsupported or corrupted image")

    # Normaliser le mode
    if im.mode in ("P", "LA"):
        im = im.convert("RGBA")
    elif im.mode == "CMYK":
        im = im.convert("RGB")

    # Redimensionnement
    if width or height:
        tw = width or im.width
        th = height or im.height

        if fit == "cover":
            im = ImageOps.fit(
                im, (tw, th),
                method=Image.Resampling.LANCZOS,
                centering=(0.5, 0.5),
            )
        elif fit == "contain":
            im.thumbnail((tw, th), resample=Image.Resampling.LANCZOS)
            # Optionnel : canvas de fond pour compléter
            if background and width and height:
                bg_rgb = _hex_to_rgb(background)
                # Si l'image a un alpha, on crée un fond RGB et on colle avec masque
                bg = Image.new("RGB", (tw, th), bg_rgb)
                x = (tw - im.width) // 2
                y = (th - im.height) // 2
                mask = im.getchannel("A") if im.mode == "RGBA" else None
                bg.paste(im.convert("RGB") if mask else im, (x, y), mask)
                im = bg
        elif fit == "fill":
            im = im.resize((tw, th), resample=Image.Resampling.LANCZOS)
        else:
            raise ValueError("Invalid fit (use cover|contain|fill)")

    # Choix du format / media-type
    fmt_l = fmt.lower()
    if fmt_l == "jpeg":
        fmt_l = "jpg"
    media_map = {
        "jpg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",
    }
    if fmt_l not in media_map:
        raise ValueError("Unsupported format")

    # Gestion alpha / aplatissement pour JPEG
    if fmt_l == "jpg":
        if im.mode == "RGBA":
            bg_rgb = _hex_to_rgb(background) if background else (255, 255, 255)
            bg = Image.new("RGB", im.size, bg_rgb)
            bg.paste(im, mask=im.split()[-1])
            im = bg
        else:
            im = im.convert("RGB")

    # Qualité bornée
    quality = max(1, min(int(quality), 100))

    # Sauvegarde en mémoire
    out = io.BytesIO()
    if fmt_l == "jpg":
        im.save(out, format="JPEG", quality=quality, optimize=True, progressive=True)
    elif fmt_l == "png":
        im.save(out, format="PNG", optimize=True)
    elif fmt_l == "webp":
        im.save(out, format="WEBP", quality=quality)
    else:
        raise ValueError("Format not handled")

    return out.getvalue(), media_map[fmt_l]
