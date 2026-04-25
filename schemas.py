from enum import IntEnum
from typing import Optional
from pydantic import BaseModel

class Role(IntEnum):
    admin = 0
    dosen = 1
    mahasiswa = 2

class Peran(IntEnum):
    ketua = 1
    sekretaris = 2
    anggota = 3
    pembimbing1 = 4
    pembimbing2 = 5

class Seminar(IntEnum):
    awal = 1
    akhir = 2

class StatusSeminar(IntEnum):
    terjadwal = 1
    selesai = 2
    batal = 3

class DataSeminar(BaseModel):
    nim: str
    jenis_seminar: Seminar
    judul_skripsi: str
    waktu_seminar: str
    ruangan: str
    status : StatusSeminar

class SeminarDosen(BaseModel):
    id_seminar: int
    id_dosen: int
    peran: Peran

class TambahSeminarRequest(BaseModel):
    nim: str
    jenis_seminar: Seminar
    judul_skripsi: str
    waktu_seminar: str
    ruangan: str
    status: StatusSeminar
    ketua_id: Optional[int] = None
    sekretaris_id: Optional[int] = None
    anggota_id: Optional[int] = None
    pembimbing1_id: Optional[int] = None
    pembimbing2_id: Optional[int] = None