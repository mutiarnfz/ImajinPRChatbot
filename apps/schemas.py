"""
Skema data:
- Pydantic models  -> validasi request masuk & bentuk response HTTP
- Gemini types.Schema -> dipakai sebagai response_schema saat memanggil model,
  supaya output Gemini selalu berbentuk JSON yang terprediksi.
"""

from google.genai import types
from pydantic import BaseModel, Field
from datetime import datetime

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


# =============================================================================
# 3) Endpoint admin — riwayat percakapan (GET /admin/conversations...)
# =============================================================================

class MessageOut(BaseModel):
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class LayananLeadOut(BaseModel):
    jenis_industri: str | None = None
    tantangan_komunikasi: str | None = None
    tujuan_bisnis: str | None = None
    estimasi_anggaran: str | None = None
    timeline: str | None = None
    rekomendasi_layanan: list[str] | None = None
    alasan_rekomendasi: str | None = None
    prioritas_lead: str | None = None
    catatan_untuk_bd: str | None = None

    model_config = {"from_attributes": True}


class ProfilQnaOut(BaseModel):
    pertanyaan: str
    jawaban: str

    model_config = {"from_attributes": True}


class ConversationSummary(BaseModel):
    id: str
    session_id: str | None = None
    jenis: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationDetail(ConversationSummary):
    messages: list[MessageOut] = []
    layanan_lead: LayananLeadOut | None = None
    profil_qna: ProfilQnaOut | None = None

    model_config = {"from_attributes": True}
