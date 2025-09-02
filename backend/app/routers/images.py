from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from app.services.convert import convert_image_bytes

router = APIRouter(tags=["images"])

@router.post("/convert")
async def convert_image(
    file: UploadFile = File(...),
    width: int | None = Form(None),
    height: int | None = Form(None),
    fit: str = Form("cover"),                 # cover | contain | fill
    fmt: str = Form("webp"),                  # jpg | png | webp
    quality: int = Form(80),
    background: str | None = Form(None),      # ex: "#ffffff"
):
    if fmt not in {"jpg", "jpeg", "png", "webp"}:
        raise HTTPException(400, "Format not supported yet (use jpg/png/webp)")

    data = await file.read()
    if not data:
        raise HTTPException(400, "Empty file")

    try:
        out_bytes, media_type = convert_image_bytes(
            data=data,
            width=width,
            height=height,
            fit=fit,
            fmt=fmt,
            quality=quality,
            background=background,
        )
    except ValueError as ve:
        raise HTTPException(400, str(ve))
    except Exception as e:
        raise HTTPException(500, f"Conversion error: {e}")

    return Response(content=out_bytes, media_type=media_type)
