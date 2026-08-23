import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

COGNODB_URI = os.getenv("COGNODB_URI", "")
COGNODB_USER = os.getenv("COGNODB_USER", "cognodb")
COGNODB_PASSWORD = os.getenv("COGNODB_PASSWORD", "")
CORS_ORIGINS = [x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if x.strip()]
