import json

from google.genai import types

from config import LAYANAN, MODEL
from gemini_client import get_client
from schemas import LeadQualificationRequest, LeadQualificationResponse, RECOMMENDATION_SCHEMA


def _build_prompt(lead: LeadQualificationRequest) -> str:
    return f"""
Anda adalah AI Business Development Analyst di sebuah agensi Public Relations.
Berdasarkan data lead qualification berikut, tentukan:

1. Layanan yang paling sesuai dari daftar (boleh lebih dari satu jika
   relevan): {", ".join(LAYANAN)}
2. Alasan singkat (2-4 kalimat) mengapa layanan tersebut paling sesuai.
3. Lead summary lengkap, termasuk penilaian prioritas lead
   (Tinggi/Sedang/Rendah) berdasarkan kejelasan tujuan bisnis, kesiapan
   anggaran, dan urgensi timeline. Sertakan juga catatan singkat untuk
   tim Business Development (mis. hal yang perlu dikonfirmasi ulang saat
   proses follow-up).

Data lead:
{json.dumps(lead.model_dump(), ensure_ascii=False, indent=2)}
""".strip()


def generate_recommendation(lead: LeadQualificationRequest) -> LeadQualificationResponse:
    client = get_client()

    response = client.models.generate_content(
        model=MODEL,
        contents=_build_prompt(lead),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=RECOMMENDATION_SCHEMA,
        ),
    )

    data = json.loads(response.text)
    return LeadQualificationResponse.model_validate(data)
