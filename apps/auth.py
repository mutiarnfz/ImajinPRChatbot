"""
Autentikasi untuk endpoint admin (riwayat percakapan).

Pendekatan saat ini: satu API key statis dikirim lewat header `X-Admin-Key`,
dicocokkan dengan ADMIN_API_KEY di environment variable. Ini level
keamanan minimal yang cukup untuk tahap awal / tool internal tim BD.

MODE DEVELOPMENT: jika ADMIN_API_KEY belum di-set sama sekali, endpoint
admin dibuka TANPA autentikasi (supaya mudah dites tanpa konfigurasi
dulu). Begitu Anda men-set ADMIN_API_KEY, pengecekan key otomatis aktif
kembali — tidak perlu ubah kode ini lagi.

⚠️  JANGAN deploy ke production tanpa ADMIN_API_KEY diisi — selama kosong,
    siapa pun bisa mengakses /admin/... dan melihat seluruh riwayat lead
    tanpa perlu login sama sekali.

Batasan lain yang perlu Anda sadari:
- Semua admin memakai key yang sama -> tidak ada audit "siapa yang akses".
- Tidak ada role granular (mis. admin vs staff BD read-only).
Kalau nanti butuh itu, upgrade ke sistem user + password/JWT (mis. dengan
fastapi-users) alih-alih satu API key untuk semua orang.
"""

from fastapi import Header, HTTPException, status

import config


def require_admin(x_admin_key: str | None = Header(None)) -> None:
    if not config.ADMIN_API_KEY:
        # Mode development: belum dikonfigurasi -> lewati pengecekan.
        print(
            "[auth] PERINGATAN: ADMIN_API_KEY belum di-set, endpoint admin "
            "terbuka tanpa autentikasi. Jangan pakai mode ini di production."
        )
        return

    if x_admin_key != config.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin key tidak valid.",
        )
