"""
Skema data:
- Pydantic models  -> validasi request masuk & bentuk response HTTP
- Gemini types.Schema -> dipakai sebagai response_schema saat memanggil model,
  supaya output Gemini selalu berbentuk JSON yang terprediksi.
"""

from google.genai import types
from pydantic import BaseModel, Field
from config import LAYANAN


# =============================================================================
# 1) Endpoint POST /layanan/
# =============================================================================

class LeadQualificationRequest(BaseModel):
    """Field yang dikirim front-end sebagai form-data ke /layanan/."""
    jenis_industri: str
    tantangan_komunikasi: str
    tujuan_bisnis: str
    estimasi_anggaran: str
    timeline: str


class LeadSummary(BaseModel):
    jenis_industri: str
    tantangan_komunikasi: str
    tujuan_bisnis: str
    estimasi_anggaran: str
    timeline: str
    prioritas_lead: str = Field(description="Tinggi / Sedang / Rendah")
    catatan_untuk_bd: str


class LeadQualificationResponse(BaseModel):
    rekomendasi_layanan: list[str]
    alasan_rekomendasi: str
    lead_summary: LeadSummary


# Schema yang dikirim ke Gemini agar output-nya JSON sesuai struktur di atas.
RECOMMENDATION_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "rekomendasi_layanan": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(type=types.Type.STRING, enum=LAYANAN),
        ),
        "alasan_rekomendasi": types.Schema(type=types.Type.STRING),
        "lead_summary": types.Schema(
            type=types.Type.OBJECT,
            properties={
                "jenis_industri": types.Schema(type=types.Type.STRING),
                "tantangan_komunikasi": types.Schema(type=types.Type.STRING),
                "tujuan_bisnis": types.Schema(type=types.Type.STRING),
                "estimasi_anggaran": types.Schema(type=types.Type.STRING),
                "timeline": types.Schema(type=types.Type.STRING),
                "prioritas_lead": types.Schema(
                    type=types.Type.STRING,
                    enum=["Tinggi", "Sedang", "Rendah"],
                ),
                "catatan_untuk_bd": types.Schema(type=types.Type.STRING),
            },
            required=[
                "jenis_industri",
                "tantangan_komunikasi",
                "tujuan_bisnis",
                "estimasi_anggaran",
                "timeline",
                "prioritas_lead",
                "catatan_untuk_bd",
            ],
        ),
    },
    required=["rekomendasi_layanan", "alasan_rekomendasi", "lead_summary"],
)


# =============================================================================
# 2) Endpoint POST /profil
# =============================================================================

class ProfilRequest(BaseModel):
    """Field yang dikirim front-end sebagai form-data ke /profil."""
    pertanyaan: str


class ProfilResponse(BaseModel):
    jawaban: str
