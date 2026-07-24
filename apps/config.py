"""
Konfigurasi terpusat aplikasi.
Semua nilai yang mungkin berubah antar-environment (project, model, path)
diletakkan di sini agar file lain tidak perlu diubah.
"""

import os

# --- Google GenAI / Vertex AI -----------------------------------------------
# Jika memakai Vertex AI backend:
PROJECT_ID = os.getenv("GENAI_PROJECT_ID", "")
LOCATION = os.getenv("GENAI_LOCATION", "")
USE_VERTEXAI = False  # set False jika memakai Gemini Developer API (pakai API_KEY)
API_KEY = os.getenv("GENAI_API_KEY", "")  # dipakai hanya jika USE_VERTEXAI = False

MODEL = os.getenv("GENAI_MODEL", "gemini-3.5-flash")  # sesuaikan dgn model tersedia

# --- Daftar layanan agensi ---------------------------------------------------
LAYANAN = [
    "Crisis Communication",
    "Media Relations",
    "Media Monitoring",
    "Stakeholder Engagement",
    "Public Relation Research",
    "Pelatihan",
]

# --- Knowledge base (profil perusahaan dari .docx) --------------------------
# Taruh satu atau beberapa file .docx berisi profil perusahaan / FAQ di sini.
# Semua file akan dibaca dan digabung sebagai konteks untuk endpoint /profil.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_DIR = os.getenv("KNOWLEDGE_DIR", os.path.join(BASE_DIR, "knowledge"))

# --- HTTP server --------------------------------------------------------------
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# --- Database (MySQL) ---------------------------------------------------------
# Sesuaikan dengan kredensial database Anda (mis. Cloud SQL, atau MySQL lokal).
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "imajinpr")

# --- Admin access ---------------------------------------------------------------
# Dipakai untuk melindungi endpoint riwayat percakapan (/admin/...).
# Wajib diisi lewat environment variable, JANGAN di-hardcode di sini.
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "")
