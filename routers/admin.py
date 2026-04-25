from fastapi import APIRouter, Form, HTTPException, status, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from models import Mahasiswa, Dosen, Seminar, SeminarDosen, get_db
from schemas import Role, SeminarDosen as SeminarDosenSchema, Peran, TambahSeminarRequest, StatusSeminar
from datetime import datetime

router = APIRouter()    

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    dosen = db.query(Dosen).filter(Dosen.role == Role.dosen).all()
    seminar = db.query(Seminar).filter(Seminar.status == StatusSeminar.terjadwal).order_by(Seminar.waktu_seminar.desc()).all()
    return templates.TemplateResponse("admin/home.html", {"request": request, "dosen": dosen, "seminar": seminar})

@router.post("/tambah-seminar")
async def tambah_seminar(request_data: TambahSeminarRequest, db: Session = Depends(get_db)):
    mahasiswa = db.query(Mahasiswa).filter(Mahasiswa.nim == request_data.nim).first()
    if not mahasiswa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Mahasiswa dengan NIM {request_data.nim} tidak ditemukan"
        )
    #Parse datetime dari string ISO format
    try:
        waktu_seminar = datetime.fromisoformat(request_data.waktu_seminar)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format waktu_seminar tidak valid. Gunakan format ISO 8601: YYYY-MM-DDTHH:MM:SS"
        )
        
    # Buat record seminar baru
    seminar_baru = Seminar(
        nim=request_data.nim,
        jenis_seminar=request_data.jenis_seminar,
        judul_skripsi=request_data.judul_skripsi,
        waktu_seminar=waktu_seminar,
        ruangan=request_data.ruangan,
        status=request_data.status
    )
    
    db.add(seminar_baru)
    db.flush()  # Dapatkan ID seminar yang baru dibuat
        
    # Mapping peran dari request
    dosen_mapping = [
        (Peran.ketua, request_data.ketua_id),
        (Peran.sekretaris, request_data.sekretaris_id),
        (Peran.anggota, request_data.anggota_id),
        (Peran.pembimbing1, request_data.pembimbing1_id),
        (Peran.pembimbing2, request_data.pembimbing2_id),
    ]
        
    try:
        for peran, dosen_id in dosen_mapping:
            seminar_dosen = SeminarDosen(
                id_seminar=seminar_baru.id,
                id_dosen=dosen_id,
                peran=peran
            )
            db.add(seminar_dosen)
    except:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Terjadi kesalahan saat menambahkan seminar")        
        
    db.commit()
    
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Data seminar berhasil ditambahkan",
        }
    )

@router.delete("/hapus-seminar/{seminar_id}")
def hapus_seminar(seminar_id: int, db: Session = Depends(get_db)):
    seminar = db.query(Seminar).filter(Seminar.id == seminar_id).first()
    if not seminar:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seminar tidak ditemukan")
    
    db.delete(seminar)
    db.commit()
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Data seminar berhasil dihapus",
        }
    )

@router.get("/seminar/{slug}", response_class=HTMLResponse)
def detail_seminar(slug: str, request: Request, db: Session = Depends(get_db)):
    seminar = db.query(Seminar).filter(Seminar.slug == slug).first()
    dosen = db.query(Dosen).filter(Dosen.role == Role.dosen).all()
    if not seminar:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seminar tidak ditemukan")
    return templates.TemplateResponse("admin/detail-seminar.html", {"request": request, "seminar": seminar, "dosen": dosen})

@router.get("/riwayat", response_class=HTMLResponse)
def riwayat(request: Request):
    return templates.TemplateResponse("admin/riwayat.html", {"request": request})

@router.get("/data-dosen", response_class=HTMLResponse)
def datadosen(request: Request, db: Session = Depends(get_db)):
    data = db.query(Dosen).filter(Dosen.role == Role.dosen).all()
    return templates.TemplateResponse("admin/data-dosen.html", {"request": request, "data": data})

@router.get("/data-mahasiswa", response_class=HTMLResponse)
def datamahasiswa(request: Request, db: Session = Depends(get_db)):
    data = db.query(Mahasiswa).limit(10).all()
    return templates.TemplateResponse("admin/data-mahasiswa.html", {"request": request, "data": data})

@router.post("/carimhs", response_class=HTMLResponse)
def cari_mahasiswa(request: Request, db: Session = Depends(get_db), cari: str = Form()):
    data = db.query(Mahasiswa).filter(Mahasiswa.nama_mahasiswa.contains(cari) | Mahasiswa.nim.contains(cari)).limit(10).all()
    return templates.TemplateResponse("admin/data-mahasiswa.html", {"request": request, "data": data})