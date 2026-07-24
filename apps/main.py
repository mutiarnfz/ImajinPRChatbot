"""
Entry point backend HTTP.

Endpoint publik:
- POST /layanan/  (form-data: jenis_industri, tantangan_komunikasi,
                    tujuan_bisnis, estimasi_anggaran, timeline,
                    session_id [opsional])
  -> rekomendasi layanan + lead summary (JSON), otomatis disimpan ke DB

- POST /profil    (form-data: pertanyaan, session_id [opsional])
  -> jawaban AI berdasarkan basis pengetahuan .docx (JSON), otomatis
     disimpan ke DB

- POST /profil/reload-knowledge
  -> memuat ulang file .docx di folder knowledge/ tanpa restart server

Endpoint admin (⚠️ SEMENTARA TANPA AUTENTIKASI — lihat catatan di bawah):
- GET /admin/conversations              -> daftar percakapan (ringkas)
- GET /admin/conversations/{id}         -> detail satu percakapan lengkap

CATATAN: pengecekan admin (`require_admin` dari auth.py) sengaja TIDAK
dipasang di endpoint di bawah untuk saat ini, atas permintaan pengembang,
supaya lebih mudah dites tanpa perlu kirim header apa pun. Ini berarti
SIAPA PUN yang bisa mengakses server ini bisa melihat seluruh riwayat
percakapan & lead. Jangan deploy ke domain publik dalam kondisi ini.

Untuk mengaktifkan kembali autentikasi admin nanti, tambahkan kembali
`dependencies=[Depends(require_admin)]` pada kedua endpoint /admin/... di
bawah, dan set environment variable ADMIN_API_KEY.

Jalankan dengan:
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"""

from fastapi import Depends, FastAPI, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload

import config
import models
from db import get_db
from knowledge_base import get_company_knowledge
from schemas import (
    ConversationDetail,
    ConversationSummary,
    LeadQualificationRequest,
    LeadQualificationResponse,
    ProfilResponse,
)
from services.lead_service import generate_recommendation
from services.qa_service import answer_question

app = FastAPI(title="AI Public Relations Consultant API")

# Sesuaikan origin sesuai domain front-end Anda di produksi.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Endpoint publik
# =============================================================================

@app.post("/layanan/", response_model=LeadQualificationResponse)
def layanan(
    jenis_industri: str = Form(...),
    tantangan_komunikasi: str = Form(...),
    tujuan_bisnis: str = Form(...),
    estimasi_anggaran: str = Form(...),
    timeline: str = Form(...),
    session_id: str | None = Form(None),
    db: Session = Depends(get_db),
):
    lead = LeadQualificationRequest(
        jenis_industri=jenis_industri,
        tantangan_komunikasi=tantangan_komunikasi,
        tujuan_bisnis=tujuan_bisnis,
        estimasi_anggaran=estimasi_anggaran,
        timeline=timeline,
    )

    try:
        result = generate_recommendation(lead)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gagal memproses rekomendasi: {e}")

    # --- Simpan percakapan ke database setelah bot merespons -----------------
    try:
        conversation = models.Conversation(session_id=session_id, jenis="layanan")
        db.add(conversation)
        db.flush()  # supaya conversation.id sudah terisi sebelum dipakai di bawah

        db.add(models.Message(
            conversation_id=conversation.id,
            role="user",
            content=lead.model_dump_json(),
        ))
        db.add(models.Message(
            conversation_id=conversation.id,
            role="bot",
            content=result.model_dump_json(),
        ))
        db.add(models.LayananLead(
            conversation_id=conversation.id,
            jenis_industri=lead.jenis_industri,
            tantangan_komunikasi=lead.tantangan_komunikasi,
            tujuan_bisnis=lead.tujuan_bisnis,
            estimasi_anggaran=lead.estimasi_anggaran,
            timeline=lead.timeline,
            rekomendasi_layanan=result.rekomendasi_layanan,
            alasan_rekomendasi=result.alasan_rekomendasi,
            prioritas_lead=result.lead_summary.prioritas_lead,
            catatan_untuk_bd=result.lead_summary.catatan_untuk_bd,
        ))
        db.commit()
    except Exception as e:
        db.rollback()
        # Respons ke pengguna tetap dikirim meski penyimpanan gagal, supaya
        # kegagalan DB tidak menggagalkan pengalaman chatbot. Tapi kita catat
        # errornya agar tim engineering tahu ada request yang tidak tersimpan.
        print(f"[main] Gagal menyimpan lead ke database: {e}")

    return result


@app.post("/profil", response_model=ProfilResponse)
def profil(
    pertanyaan: str = Form(...),
    session_id: str | None = Form(None),
    db: Session = Depends(get_db),
):
    try:
        jawaban = answer_question(pertanyaan)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gagal menjawab pertanyaan: {e}")

    try:
        conversation = models.Conversation(session_id=session_id, jenis="profil")
        db.add(conversation)
        db.flush()

        db.add(models.Message(conversation_id=conversation.id, role="user", content=pertanyaan))
        db.add(models.Message(conversation_id=conversation.id, role="bot", content=jawaban))
        db.add(models.ProfilQna(
            conversation_id=conversation.id,
            pertanyaan=pertanyaan,
            jawaban=jawaban,
        ))
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[main] Gagal menyimpan Q&A ke database: {e}")

    return ProfilResponse(jawaban=jawaban)


@app.post("/profil/reload-knowledge")
def reload_knowledge(db: Session = Depends(get_db)):
    """Panggil endpoint ini setelah menambah/mengubah file .docx di folder
    knowledge/ agar AI langsung memakai versi terbaru tanpa restart server."""
    knowledge = get_company_knowledge(force_reload=True)

    try:
        db.add(models.KnowledgeReloadLog(panjang_konteks_karakter=len(knowledge)))
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[main] Gagal mencatat log reload knowledge: {e}")

    return {"status": "ok", "panjang_konteks_karakter": len(knowledge)}


@app.get("/health")
def health():
    return {"status": "ok", "model": config.MODEL}


# =============================================================================
# Endpoint admin — riwayat percakapan
# =============================================================================

@app.get(
    "/admin/conversations",
    response_model=list[ConversationSummary],
)
def list_conversations(
    jenis: str | None = Query(None, description="Filter: 'layanan' atau 'profil'"),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(models.Conversation)
    if jenis:
        query = query.filter(models.Conversation.jenis == jenis)
    return (
        query.order_by(models.Conversation.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@app.get(
    "/admin/conversations/{conversation_id}",
    response_model=ConversationDetail,
)
def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    conversation = (
        db.query(models.Conversation)
        .options(
            joinedload(models.Conversation.messages),
            joinedload(models.Conversation.layanan_lead),
            joinedload(models.Conversation.profil_qna),
        )
        .filter(models.Conversation.id == conversation_id)
        .first()
    )
    if conversation is None:
        raise HTTPException(status_code=404, detail="Percakapan tidak ditemukan.")
    return conversation
