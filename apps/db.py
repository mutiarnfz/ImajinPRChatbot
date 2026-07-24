"""
Koneksi database (MySQL) memakai SQLAlchemy.

Menyediakan:
- `engine`   : koneksi pool ke MySQL
- `Base`     : base class untuk model ORM (lihat models.py)
- `get_db()` : FastAPI dependency, membuka satu session per-request dan
               memastikan session ditutup setelah request selesai
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

import config

DATABASE_URL = (
    f"mysql+pymysql://{config.DB_USER}:{config.DB_PASSWORD}"
    f"@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
)

# pool_pre_ping=True -> otomatis cek & buka ulang koneksi yang sudah mati
# (mis. karena idle timeout di server MySQL), supaya tidak error di request
# pertama setelah server nganggur lama.
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
