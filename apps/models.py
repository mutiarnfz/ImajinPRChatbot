"""
Model SQLAlchemy ORM — mengikuti persis struktur `schema.sql`.

Catatan: kolom id di schema.sql memakai DEFAULT (UUID()) sisi MySQL.
Di sini default UUID dibuat di sisi Python (`default=_new_uuid`) supaya
nilainya sudah tersedia sebelum commit (berguna untuk langsung memakai
`conversation.id` saat insert baris anak di request yang sama), tapi
tetap kompatibel dengan kolom CHAR(36) di database.
"""

import uuid

from sqlalchemy import (
    Column,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    TIMESTAMP,
    func,
)
from sqlalchemy.orm import relationship

from db import Base


def _new_uuid() -> str:
    return str(uuid.uuid4())


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=_new_uuid)
    session_id = Column(String(255), nullable=True)
    jenis = Column(Enum("layanan", "profil", name="jenis_enum"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    messages = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )
    layanan_lead = relationship(
        "LayananLead",
        back_populates="conversation",
        uselist=False,
        cascade="all, delete-orphan",
    )
    profil_qna = relationship(
        "ProfilQna",
        back_populates="conversation",
        uselist=False,
        cascade="all, delete-orphan",
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=_new_uuid)
    conversation_id = Column(
        String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    role = Column(Enum("user", "bot", name="role_enum"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")


class LayananLead(Base):
    __tablename__ = "layanan_leads"

    id = Column(String(36), primary_key=True, default=_new_uuid)
    conversation_id = Column(
        String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    jenis_industri = Column(String(100))
    tantangan_komunikasi = Column(Text)
    tujuan_bisnis = Column(Text)
    estimasi_anggaran = Column(String(100))
    timeline = Column(String(50))
    rekomendasi_layanan = Column(JSON)
    alasan_rekomendasi = Column(Text)
    prioritas_lead = Column(Enum("Rendah", "Sedang", "Tinggi", name="prioritas_enum"))
    catatan_untuk_bd = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    conversation = relationship("Conversation", back_populates="layanan_lead")


class ProfilQna(Base):
    __tablename__ = "profil_qna"

    id = Column(String(36), primary_key=True, default=_new_uuid)
    conversation_id = Column(
        String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    pertanyaan = Column(Text, nullable=False)
    jawaban = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    conversation = relationship("Conversation", back_populates="profil_qna")


class KnowledgeReloadLog(Base):
    __tablename__ = "knowledge_reload_logs"

    id = Column(String(36), primary_key=True, default=_new_uuid)
    panjang_konteks_karakter = Column(Integer)
    triggered_at = Column(TIMESTAMP, server_default=func.now())
