from sqlalchemy import Column, Float, ForeignKey, Integer, String, Enum, DateTime
from schemas import Role, Peran, Seminar as SeminarType, StatusSeminar
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from sqlalchemy import create_engine
from dotenv import load_dotenv
import uuid
from database_config import get_database_url

load_dotenv()

# --- Config ---
#SQLALCHEMY_DATABASE_URL = "sqlite:///testdb.sqlite3"

SQLALCHEMY_DATABASE_URL = get_database_url()
Base = declarative_base()

def get_engine():
    db_url = SQLALCHEMY_DATABASE_URL
    if db_url.startswith('sqlite'):
        # SQLite specific configuration
        return create_engine(
            db_url, 
            connect_args={"check_same_thread": False}
        )
    else:
        # MySQL configuration
        return create_engine(db_url)

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -- Models ---
class Dosen(Base):
    __tablename__ = "dosen"
    id = Column(Integer, primary_key=True)
    nip = Column(String(20), unique=True)
    nama_dosen = Column(String(100), nullable=False)
    role = Column(Enum(Role), default=Role.dosen)
    email = Column(String(100), unique=True)
    password = Column(String(255))
    seminar_roles = relationship("SeminarDosen", back_populates="dosen")

class Mahasiswa(Base):
    __tablename__ = "mahasiswa"
    nim = Column(String(20), primary_key=True)
    nama_mahasiswa = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    nohp = Column(String(14), unique=True)
    program_studi = Column(String(100))
    seminars = relationship("Seminar", back_populates="mahasiswa")

class Seminar(Base):
    __tablename__ = "seminar"
    id = Column(Integer, primary_key=True)
    nim = Column(String(20), ForeignKey("mahasiswa.nim"))
    jenis_seminar = Column(Enum(SeminarType))
    judul_skripsi = Column(String(255))
    waktu_seminar = Column(DateTime)
    ruangan = Column(String(50))
    status = Column(Enum(StatusSeminar), default=StatusSeminar.terjadwal)
    slug = Column(String(255), default=lambda:uuid.uuid4().hex, unique=True, index=True)
    mahasiswa = relationship("Mahasiswa", back_populates="seminars")
    dosen_roles = relationship("SeminarDosen", back_populates="seminar")
    hasil = relationship("HasilSeminar", back_populates="seminar", uselist=False)

class SeminarDosen(Base):
    __tablename__ = "seminar_dosen"
    id = Column(Integer, primary_key=True)
    id_seminar = Column(Integer, ForeignKey("seminar.id", ondelete="CASCADE"))
    id_dosen = Column(Integer, ForeignKey("dosen.id"))
    peran = Column(Enum(Peran))
    seminar = relationship("Seminar", back_populates="dosen_roles")
    dosen = relationship("Dosen", back_populates="seminar_roles")
    penilaian = relationship("Penilaian", back_populates="seminar_dosen")

class KomponenNilai(Base):
    __tablename__ = "komponen_nilai"
    id_komponen = Column(Integer, primary_key=True)
    kode_komponen = Column(String(2))
    urutan = Column(Integer, unique=True)
    nama_komponen = Column(String(100))
    penilaian = relationship("Penilaian", back_populates="komponen")

class Penilaian(Base):
    __tablename__ = "penilaian"
    id_penilaian = Column(Integer, primary_key=True)
    id_seminar_dosen = Column(Integer, ForeignKey("seminar_dosen.id", ondelete="CASCADE"))
    id_komponen = Column(Integer, ForeignKey("komponen_nilai.id_komponen", ondelete="CASCADE"))
    nilai = Column(Integer, default=0)
    seminar_dosen = relationship("SeminarDosen", back_populates="penilaian")
    komponen = relationship("KomponenNilai", back_populates="penilaian")

class HasilSeminar(Base):
    __tablename__ = "hasil_seminar"
    id_hasil = Column(Integer, primary_key=True)
    id_seminar = Column(Integer, ForeignKey("seminar.id", ondelete="CASCADE"))
    nilai_akhir = Column(Float)
    grade = Column(String(2))
    seminar = relationship("Seminar", back_populates="hasil")