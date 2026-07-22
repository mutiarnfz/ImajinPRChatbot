import os

PROJECT_ID = os.getenv("GENAI_PROJECT_ID", "")
USE_VERTEXAI = False  # set False jika memakai Gemini Developer API (pakai API_KEY)
API_KEY = os.getenv("GENAI_API_KEY", "")  # dipakai hanya jika USE_VERTEXAI = False

MODEL = os.getenv("GENAI_MODEL", "gemini-3.5-flash")  

LAYANAN = [
    "Crisis Communication",
    "Media Relations",
    "Media Monitoring",
    "Stakeholder Engagement",
    "Public Relation Research",
    "Pelatihan",
]

# --- Knowledge base --------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_DIR = os.getenv("KNOWLEDGE_DIR", os.path.join(BASE_DIR, "knowledge"))

# --- HTTP server --------------------------------------------------------------
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
