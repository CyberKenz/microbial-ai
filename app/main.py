"""
FastAPI server for Microba Segmentation Model.

Endpoints:
  GET  /api/health          - Health check and model status
  POST /api/predict         - Upload image, get JSON detection results
  POST /api/predict-annotated - Upload image, get annotated image with masks/boxes
"""

import io
import time
import logging
from contextlib import asynccontextmanager
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse

from app.config import (
    MODEL_PATH,
    CONFIDENCE_THRESHOLD,
    IOU_THRESHOLD,
    IMG_SIZE,
    MAX_DETECTIONS,
    HOST,
    PORT,
    CORS_ORIGINS,
    CLASS_NAMES,
    DEFAULT_VOLUME_PLATED_ML,
    DEFAULT_DILUTION_FACTOR,
)

# ---------------------------------------------------------------------------
# Logger
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("microba_api")

# ---------------------------------------------------------------------------
# Global model reference
# ---------------------------------------------------------------------------
model = None


# ---------------------------------------------------------------------------
# Lifespan: load/unload model
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the YOLO model at startup."""
    global model
    logger.info(f"Loading model from: {MODEL_PATH}")
    try:
        from ultralytics import YOLO
        model = YOLO(MODEL_PATH)
        logger.info("Model loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        model = None
    yield
    model = None
    logger.info("Model unloaded.")


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Microba Segmentation API",
    description="API for detecting isolated and clustered microba using YOLO segmentation.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helper: validate and decode uploaded image
# ---------------------------------------------------------------------------
async def _decode_image(file: UploadFile) -> np.ndarray:
    """Read an uploaded file into a BGR numpy array."""
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image.")

    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Decode with OpenCV
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Could not decode image. Supported formats: JPG, PNG, BMP, TIFF.")
    return img


# ---------------------------------------------------------------------------
# Helper: run inference
# ---------------------------------------------------------------------------
def _run_inference(img: np.ndarray):
    """Run the YOLO model on a BGR image and return the results object."""
    if model is None:
        raise HTTPException(status_code=503, detail="Model is not loaded. Check server logs.")

    results = model.predict(
        source=img,
        conf=CONFIDENCE_THRESHOLD,
        iou=IOU_THRESHOLD,
        imgsz=IMG_SIZE,
        max_det=MAX_DETECTIONS,
        verbose=False,
    )
    return results


# ---------------------------------------------------------------------------
# Helper: extract detections from results
# ---------------------------------------------------------------------------
def _extract_detections(results, orig_h: int, orig_w: int) -> dict:
    """Parse ultralytics results into a clean JSON-serialisable dict."""
    detections = []
    r = results[0]

    if r.boxes is not None and r.masks is not None:
        boxes = r.boxes
        masks = r.masks

        for i in range(len(boxes)):
            # Bounding box (x1, y1, x2, y2) in original image coords
            x1, y1, x2, y2 = boxes.xyxy[i].tolist()

            # Confidence
            conf = float(boxes.conf[i])

            # Class
            cls_id = int(boxes.cls[i])
            cls_name = CLASS_NAMES.get(cls_id, f"class_{cls_id}")

            # Mask polygon points (in original image coords)
            mask_polygon = []
            if masks.xyn is not None and i < len(masks.xyn):
                # xyn = normalised polygon points; convert to pixel coords
                for segment in masks.xyn[i]:
                    px, py = float(segment[0]) * orig_w, float(segment[1]) * orig_h
                    mask_polygon.append([round(px, 2), round(py, 2)])

            detections.append({
                "class": cls_name,
                "confidence": round(conf, 4),
                "bbox": [round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)],
                "mask": mask_polygon,
            })

    return {
        "detections": detections,
        "summary": {
            "total_detections": len(detections),
            "isolated_microba": sum(1 for d in detections if d["class"] == "isolated_microba"),
            "clustered_microba": sum(1 for d in detections if d["class"] == "clustered_microba"),
        },
        "image_size": {"width": orig_w, "height": orig_h},
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Microba Segmentation API", "docs": "/docs"}


@app.get("/api/health")
async def health():
    """Health check. Returns model loading status."""
    model_loaded = model is not None
    return JSONResponse(
        status_code=200 if model_loaded else 503,
        content={
            "status": "healthy" if model_loaded else "model_not_loaded",
            "model_loaded": model_loaded,
            "model_path": MODEL_PATH,
            "config": {
                "confidence_threshold": CONFIDENCE_THRESHOLD,
                "iou_threshold": IOU_THRESHOLD,
                "img_size": IMG_SIZE,
                "max_detections": MAX_DETECTIONS,
            },
        },
    )


@app.post("/api/predict")
async def predict(file: UploadFile = File(...)):
    """
    Upload an image and receive JSON segmentation results.

    Returns bounding boxes, mask polygons, confidence scores, and class labels.
    """
    img = await _decode_image(file)
    orig_h, orig_w = img.shape[:2]

    t0 = time.time()
    results = _run_inference(img)
    inference_ms = round((time.time() - t0) * 1000, 2)

    data = _extract_detections(results, orig_h, orig_w)
    data["inference_time_ms"] = inference_ms

    return JSONResponse(content=data)


@app.post("/api/predict-annotated")
async def predict_annotated(file: UploadFile = File(...)):
    """
    Upload an image and receive an annotated image (PNG) with bounding boxes
    and segmentation masks drawn on top — color-coded by class, no text labels,
    with a legend at the bottom.
    """
    img = await _decode_image(file)
    orig_h, orig_w = img.shape[:2]

    results = _run_inference(img)
    annotated = _draw_annotations(results[0], img.copy(), orig_h, orig_w)

    # Encode to PNG
    success, buf = cv2.imencode(".png", annotated)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to encode annotated image.")

    return Response(content=buf.tobytes(), media_type="image/png")


# ---------------------------------------------------------------------------
# Custom annotation drawing (no class text on detections)
# ---------------------------------------------------------------------------

# BGR colours for each class
_CLASS_COLORS = {
    "isolated_microba": (255, 150, 50),    # blue-ish
    "clustered_microba": (180, 50, 220),   # magenta/pink
}
_CLASS_DISPLAY = {
    "isolated_microba": "Isolated",
    "clustered_microba": "Clustered",
}


def _draw_annotations(result, img: np.ndarray, orig_h: int, orig_w: int) -> np.ndarray:
    """Draw segmentation masks + bounding boxes (colour-coded, no labels) and a legend."""
    overlay = img.copy()

    if result.boxes is None or result.masks is None:
        return img

    boxes = result.boxes
    masks = result.masks
    class_counts = {}

    # --- Draw masks and bboxes ---
    for i in range(len(boxes)):
        cls_id = int(boxes.cls[i])
        cls_name = CLASS_NAMES.get(cls_id, f"class_{cls_id}")
        color = _CLASS_COLORS.get(cls_name, (200, 200, 200))
        class_counts[cls_name] = class_counts.get(cls_name, 0) + 1

        # --- Mask (semi-transparent fill) ---
        if masks.data is not None and i < len(masks.data):
            # masks.data shape: (N, mask_h, mask_w) — at model resolution
            mask_tensor = masks.data[i].cpu().numpy()
            # Resize mask to original image size
            mask_resized = cv2.resize(mask_tensor, (orig_w, orig_h), interpolation=cv2.INTER_LINEAR)
            mask_bool = (mask_resized > 0.5).astype(np.uint8)

            # Create coloured mask overlay
            colored_mask = np.zeros_like(overlay, dtype=np.uint8)
            colored_mask[:, :] = color
            # Apply mask with alpha blending
            alpha = 0.35
            mask_idx = mask_bool == 1
            overlay[mask_idx] = (
                (1 - alpha) * overlay[mask_idx].astype(np.float32)
                + alpha * np.array(color, dtype=np.float32)
            ).astype(np.uint8)

        # --- Bounding box ---
        x1, y1, x2, y2 = boxes.xyxy[i].tolist()
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 2)

    # --- Legend bar at bottom ---
    legend_h = 40
    legend_bar = np.ones((legend_h, orig_w, 3), dtype=np.uint8) * 30  # dark background

    x_offset = 15
    for cls_name, display in _CLASS_DISPLAY.items():
        color = _CLASS_COLORS.get(cls_name, (200, 200, 200))
        count = class_counts.get(cls_name, 0)

        # Colour swatch
        cv2.rectangle(legend_bar, (x_offset, 8), (x_offset + 18, 30), color, -1)
        cv2.rectangle(legend_bar, (x_offset, 8), (x_offset + 18, 30), (255, 255, 255), 1)
        x_offset += 24

        # Text: "Isolated (158)"
        label = f"{display} ({count})"
        cv2.putText(
            legend_bar, label, (x_offset, 26),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA,
        )
        x_offset += cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)[0][0] + 30

    # Stack legend below image
    annotated = np.vstack([overlay, legend_bar])
    return annotated


# ---------------------------------------------------------------------------
# CFU/ml calculation
# ---------------------------------------------------------------------------

@app.get("/api/cfu-defaults")
async def cfu_defaults():
    """Return the default CFU/ml calculation parameters."""
    return {
        "default_volume_plated_ml": DEFAULT_VOLUME_PLATED_ML,
        "default_dilution_factor": DEFAULT_DILUTION_FACTOR,
    }


@app.post("/api/calculate-cfu")
async def calculate_cfu(file: UploadFile = File(...), volume_plated_ml: float = None, dilution_factor: float = None):
    """
    Upload an image, run detection, and calculate CFU/ml.

    Formula: CFU/ml = total_colonies / (volume_plated_ml × dilution_factor)

    Query parameters:
      - volume_plated_ml: volume plated in ml (default from config)
      - dilution_factor: dilution factor as decimal (e.g. 0.00001 for 10^-5)
    """
    vol = volume_plated_ml if volume_plated_ml is not None else DEFAULT_VOLUME_PLATED_ML
    dil = dilution_factor if dilution_factor is not None else DEFAULT_DILUTION_FACTOR

    if vol <= 0:
        raise HTTPException(status_code=400, detail="volume_plated_ml must be > 0")
    if dil <= 0:
        raise HTTPException(status_code=400, detail="dilution_factor must be > 0")

    img = await _decode_image(file)
    orig_h, orig_w = img.shape[:2]

    t0 = time.time()
    results = _run_inference(img)
    inference_ms = round((time.time() - t0) * 1000, 2)

    data = _extract_detections(results, orig_h, orig_w)
    data["inference_time_ms"] = inference_ms

    # CFU/ml calculation
    total_colonies = data["summary"]["total_detections"]
    cfu_per_ml = total_colonies / (vol * dil) if total_colonies > 0 else 0

    data["cfu_calculation"] = {
        "total_colonies": total_colonies,
        "volume_plated_ml": vol,
        "dilution_factor": dil,
        "dilution_display": _dilution_display(dil),
        "cfu_per_ml": round(cfu_per_ml, 2),
        "cfu_per_ml_scientific": f"{cfu_per_ml:.2e}",
        "formula": "CFU/ml = total_colonies / (volume_plated_ml × dilution_factor)",
        "formula_values": f"CFU/ml = {total_colonies} / ({vol} × {dil}) = {cfu_per_ml:.2e}",
    }

    return JSONResponse(content=data)


def _dilution_display(dil: float) -> str:
    """Convert dilution decimal to human-readable format like '10^-5'."""
    import math
    if dil <= 0:
        return str(dil)
    exp = round(math.log10(dil))
    if 10 ** exp == dil:
        if exp == 0:
            return "10^0 (no dilution)"
        return f"10^{exp}"
    return f"{dil}"


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host=HOST, port=PORT, reload=False)
