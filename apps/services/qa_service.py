from google.genai import types

from config import MODEL
from gemini_client import get_client
from knowledge_base import get_company_knowledge


def _build_system_prompt() -> str:
    knowledge = get_company_knowledge()

    if knowledge:
        context_block = f"""
Berikut adalah informasi resmi tentang perusahaan yang HARUS Anda jadikan
rujukan utama saat menjawab. Jika jawaban tidak ditemukan di informasi ini,
katakan dengan jujur bahwa Anda belum memiliki informasinya, jangan mengarang.

--- MULAI INFORMASI PERUSAHAAN ---
{knowledge}
--- SELESAI INFORMASI PERUSAHAAN ---
"""
    else:
        context_block = (
            "Catatan: belum ada dokumen profil perusahaan yang dimuat. "
            "Jawab secara umum dan sarankan pengguna menghubungi tim terkait "
            "untuk info spesifik."
        )

    return f"""
Anda adalah AI Public Relations Consultant yang ramah dan informatif,
mewakili sebuah agensi PR. Jawab pertanyaan pengguna seputar profil
perusahaan, layanan, dan public relations secara singkat, jelas, dan
akurat.

{context_block}
""".strip()


def answer_question(pertanyaan: str) -> str:
    client = get_client()

    response = client.models.generate_content(
        model=MODEL,
        contents=pertanyaan,
        config=types.GenerateContentConfig(
            system_instruction=_build_system_prompt(),
        ),
    )
    return response.text
