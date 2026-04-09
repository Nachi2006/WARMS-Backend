import os
import asyncio
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from auth.auth import get_current_user_token

router = APIRouter(prefix="/species", tags=["Species AI"])

_model = None

def _load_model():
    global _model
    if _model is None:
        try:
            from speciesnet import SpeciesNet
            _model = SpeciesNet()
        except Exception as e:
            raise RuntimeError(f"Failed to load SpeciesNet model: {e}")
    return _model

async def _run_inference(image_bytes: bytes) -> dict:
    import tempfile

    def _infer():
        model = _load_model()
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp.write(image_bytes)
            tmp_path = tmp.name
        try:
            result = model.predict(tmp_path)
            return result
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    return await asyncio.wait_for(
        asyncio.to_thread(_infer),
        timeout=10.0
    )

@router.post("/identify-species", tags=["Species AI"])
async def identify_species(
    image: UploadFile = File(...),
    token_data: dict = Depends(get_current_user_token)
):
    allowed_types = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uploaded file must be a valid image (JPEG, PNG, WEBP, GIF)"
        )

    image_bytes = await image.read()
    if len(image_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uploaded image is empty"
        )

    try:
        result = await _run_inference(image_bytes)
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Species identification timed out after 10 seconds"
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference failed: {str(e)}"
        )

    if isinstance(result, dict):
        species = result.get("species") or result.get("label") or result.get("class", "Unknown")
        confidence = result.get("confidence") or result.get("score", 0.0)
    elif isinstance(result, (list, tuple)) and len(result) >= 2:
        species, confidence = str(result[0]), float(result[1])
    else:
        species = str(result)
        confidence = 0.0

    return {
        "species": species,
        "confidence": round(float(confidence), 4),
        "filename": image.filename
    }
