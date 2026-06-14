"""
Configuration settings for the Microba Segmentation API.
"""

import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# Model configuration
MODEL_PATH = os.getenv(
    "MODEL_PATH",
    str(PROJECT_ROOT / "model" / "best.pt"),
)

# Inference settings
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.25"))
IOU_THRESHOLD = float(os.getenv("IOU_THRESHOLD", "0.7"))
IMG_SIZE = int(os.getenv("IMG_SIZE", "1280"))
MAX_DETECTIONS = int(os.getenv("MAX_DETECTIONS", "500"))

# Server settings
HOST = os.getenv("API_HOST", "0.0.0.0")
PORT = int(os.getenv("API_PORT", "8000"))

# CORS origins (comma-separated)
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:4173,https://microbialai.vercel.app",
).split(",")

# Class names from the trained model
# Training data analysis:
#   Class 0 (n=5748): avg_area=0.00174, median=0.00042 → small individual colonies
#   Class 1 (n=105):  avg_area=0.00640, median=0.00041 → larger clustered regions
# Definitions:
#   "isolated"  = single, separated colonies (smaller bounding areas)
#   "clustered" = grouped, adjacent colonies (larger bounding areas)
CLASS_NAMES = {
    0: "isolated_microba",
    1: "clustered_microba",
}

# CFU/ml calculation defaults
# Standard plate count formula: CFU/ml = (total colonies) / (volume_plated_ml × dilution_factor)
DEFAULT_VOLUME_PLATED_ML = float(os.getenv("DEFAULT_VOLUME_PLATED_ML", "0.1"))
DEFAULT_DILUTION_FACTOR = float(os.getenv("DEFAULT_DILUTION_FACTOR", "0.00001"))  # 10^-5
