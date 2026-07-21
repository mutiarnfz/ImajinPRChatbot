from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import config
from knowledge_base import get_company_knowledge
from schemas import LeadQualificationRequest, LeadQualificationResponse, ProfilResponse
from services.lead_service import generate_recommendation
from services.qa_service import answer_question

app = FastAPI(title="AI Public Relations Consultant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/layanan/", response_model=LeadQualificationResponse)
def layanan(
    jenis_industri: str = Form(...),
    tantangan_komunikasi: str = Form(...),
    tujuan_bisnis: str = Form(...),
    estimasi_anggaran: str = Form(...),
    timeline: str = Form(...),
):
    lead = LeadQualificationRequest(
        jenis_industri=jenis_industri,
        tantangan_komunikasi=tantangan_komunikasi,
        tujuan_bisnis=tujuan_bisnis,
        estimasi_anggaran=estimasi_anggaran,
        timeline=timeline,
    )
    try:
        return generate_recommendation(lead)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gagal memproses rekomendasi: {e}")


@app.post("/profil", response_model=ProfilResponse)
def profil(pertanyaan: str = Form(...)):
    try:
        jawaban = answer_question(pertanyaan)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gagal menjawab pertanyaan: {e}")
    return ProfilResponse(jawaban=jawaban)


@app.post("/profil/reload-knowledge")
def reload_knowledge():
    """Panggil endpoint ini setelah menambah/mengubah file .docx di folder
    knowledge/ agar AI langsung memakai versi terbaru tanpa restart server."""
    knowledge = get_company_knowledge(force_reload=True)
    return {"status": "ok", "panjang_konteks_karakter": len(knowledge)}


@app.get("/health")
def health():
    return {"status": "ok", "model": config.MODEL}
