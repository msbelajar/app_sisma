from fastapi import APIRouter, HTTPException, UploadFile, status, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import and_
from models import get_db, Dosen, Seminar, SeminarDosen, Penilaian, HasilSeminar
from security import user_cookies, checkpass, genpass
from schemas import StatusSeminar, KomNilaiSem, Peran, UbahPassword, UbahProfil
from utils import get_grade, allowed_extension, validate_magic_bytes, UPLOAD_DIR, ALLOWED_MIME_TYPES, MAX_FILE_SIZE
from werkzeug.utils import secure_filename
import os
import uuid

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def dosen_dashboard(request: Request, db: Session = Depends(get_db), data = Depends(user_cookies)):
    nip = data.get("sub")
    dosen = db.query(Dosen).filter(Dosen.nip == nip).first()
    # seminar = db.query(SeminarDosen).filter(SeminarDosen.id_dosen == dosen.id).order_by(Seminar.waktu_seminar.desc()).all()
    seminar = db.query(SeminarDosen).join(Seminar, Seminar.id == SeminarDosen.id_seminar).filter(and_(SeminarDosen.id_dosen == dosen.id, Seminar.status == StatusSeminar.terjadwal)).all()
    return templates.TemplateResponse("user/home.html", {"request": request, "data": seminar})

@router.get("/seminar-final", response_class=HTMLResponse)
def seminar_final(request: Request, db: Session = Depends(get_db), data = Depends(user_cookies)):
    nip = data.get("sub")
    dosen = db.query(Dosen).filter(Dosen.nip == nip).first()
    seminar = db.query(SeminarDosen).join(Seminar, Seminar.id == SeminarDosen.id_seminar).filter(and_(SeminarDosen.id_dosen == dosen.id, Seminar.status == StatusSeminar.final)).all()
    return templates.TemplateResponse("user/home.html", {"request": request, "data": seminar, "status": "telah Finalisasi Nilai"})

@router.get("/profil", response_class=HTMLResponse)
def dosen_profil(request: Request, db: Session = Depends(get_db), data = Depends(user_cookies)):
    nip = data.get("sub")
    dosen = db.query(Dosen).filter(Dosen.nip == nip).first()
    return templates.TemplateResponse("user/profil.html", {"request": request, "dosen": dosen})

@router.put("/ubahprofil")
def ubah_profil(data: UbahProfil, db: Session = Depends(get_db), user = Depends(user_cookies)): 
    nip = user.get("sub")
    print(data)
    dosen = db.query(Dosen).filter(Dosen.nip == nip).first()
    if not dosen:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dosen tidak ditemukan")
    try:
        dosen.nip = data.nip
        dosen.nama_dosen = data.nama_dosen
        db.commit()
        return {"message": "Profil berhasil diubah"}
    except:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="gagal ubah profil")
    
@router.put("/ubahpassword")
def ubah_password(data: UbahPassword, db: Session = Depends(get_db), user = Depends(user_cookies)):
    nip = user.get("sub")
    dosen = db.query(Dosen).filter(Dosen.nip == nip).first()
    if not dosen:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dosen tidak ditemukan")
    if not checkpass(data.password_lama, dosen.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password lama salah")
    try:
        dosen.password = genpass(data.password_baru)
        db.commit()
        return {"message": "Password berhasil diubah"}
    except:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="gagal ubah password")

@router.post("/uploadttd")
async def upload_file_ttd(file: UploadFile, user = Depends(user_cookies), db = Depends(get_db)):
    nip = user.get("sub")
    dosen = db.query(Dosen).filter(Dosen.nip == nip).first()
    if not dosen:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dosen tidak ditemukan")
    try:
        # 1. Validasi namafile
        original_filename = file.filename
        if not original_filename:
            raise HTTPException(status_code=400,detail="Filename is missing")
        # bersihkan nama file
        safe_filename = secure_filename(original_filename)

        if not allowed_extension(safe_filename):
            raise HTTPException(status_code=400,detail="Only JPG, JPEG, PNG files are allowed")
        # 2. Validasi MIME type
        if file.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(status_code=400,detail="Invalid MIME type")
        # 3. Baca file
        file_bytes = await file.read()
        # 4. Validasi ukuran file
        if len(file_bytes) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400,detail="File too large (max 200KB)")
        # 5. Validasi magic bytes
        if not validate_magic_bytes(file_bytes):
            raise HTTPException(status_code=400,detail="File content is invalid")
        # 6. Rename acak pakai UUID
        ext = safe_filename.rsplit(".", 1)[1].lower()
        random_filename = f"{uuid.uuid4()}.{ext}"
        file_path = os.path.join(UPLOAD_DIR, random_filename)
        # 7. hapus file lama jika ada
        if dosen.tandatangan:
            old_file_path = os.path.join(UPLOAD_DIR, dosen.tandatangan)
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
        # 8. Simpan file baru
        with open(file_path, "wb") as buffer:
            buffer.write(file_bytes)
        # Update the dosen's tandatangan field
        dosen.tandatangan = random_filename
        db.commit()
        return {"message": "Tanda tangan berhasil diupload"}

    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Gagal upload file: {str(e)}")
    

@router.get("/lihatsign/{filename}", response_class=FileResponse)
async def upload_file_ttd(filename: str, user = Depends(user_cookies), db = Depends(get_db)):
    nip = user.get("sub")
    dosen = db.query(Dosen).filter(Dosen.nip == nip).first()
    if not dosen:
        raise HTTPException(status_code=400, detail="not found")
    file_path = os.path.join(UPLOAD_DIR,filename)
    return FileResponse(path=file_path,filename=filename)


@router.post("/kirimnilai/{slug}")
def tambah_seminar(slug: str, data: KomNilaiSem, db: Session = Depends(get_db), user = Depends(user_cookies)):
    nip = user.get("sub")
    dtdosen = db.query(Dosen).filter(Dosen.nip == nip).first()
    seminar = db.query(Seminar).filter(Seminar.slug == slug).first()
    semdos = db.query(SeminarDosen).filter(and_(SeminarDosen.id_dosen == dtdosen.id, SeminarDosen.id_seminar == seminar.id)).first()
    check = db.query(Penilaian).filter(Penilaian.id_seminar_dosen == semdos.id).first()
    if check:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nilai sudah ada")    
    try:
        _npen = Penilaian(id_seminar_dosen=semdos.id, id_komponen=1, nilai=data.penulisan)
        _nmat = Penilaian(id_seminar_dosen=semdos.id, id_komponen=2, nilai=data.materi)
        _nsaji = Penilaian(id_seminar_dosen=semdos.id, id_komponen=3, nilai=data.penyajian)
        _nbim = Penilaian(id_seminar_dosen=semdos.id, id_komponen=4, nilai=data.pembimbingan)
        db.add_all([_npen, _nmat, _nsaji, _nbim])
        db.commit()
        return {"message": "Nilai berhasil dikirim"}
    except:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="gagal kirim nilai")
    

@router.put("/updatenilai/{slug}")
async def update_nilai(slug: str, data: KomNilaiSem, db: Session = Depends(get_db), user = Depends(user_cookies)):
    nip = user.get("sub")
    dtdosen = db.query(Dosen).filter(Dosen.nip == nip).first()
    seminar = db.query(Seminar).filter(Seminar.slug == slug).first()
    semdos = db.query(SeminarDosen).filter(and_(SeminarDosen.id_dosen == dtdosen.id, SeminarDosen.id_seminar == seminar.id)).first()
    penilaian = db.query(Penilaian).filter(Penilaian.id_seminar_dosen == semdos.id).all()
    if not penilaian:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nilai tidak ditemukan")
    try:
        for p in penilaian:
            if p.id_komponen == 1:
                p.nilai = data.penulisan
            elif p.id_komponen == 2:
                p.nilai = data.materi
            elif p.id_komponen == 3:
                p.nilai = data.penyajian
            elif p.id_komponen == 4:
                p.nilai = data.pembimbingan
        db.commit()
    except:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="gagal update nilai")


@router.get("/penilaian/{slug}", response_class=HTMLResponse)
def penilaian(slug: str, request: Request, db: Session = Depends(get_db), user = Depends(user_cookies)):
    #perlu tambahan cek nip dan role
    nip = user.get("sub")
    role = user.get("role")
    dtdosen = db.query(Dosen).filter(Dosen.nip == nip).first()
    seminar = db.query(Seminar).filter(Seminar.slug == slug).first()
    dosen = db.query(SeminarDosen).filter(and_(SeminarDosen.id_dosen == dtdosen.id, SeminarDosen.id_seminar == seminar.id)).first()
    penilaian = db.query(Penilaian).filter(Penilaian.id_seminar_dosen == dosen.id).first()
    return templates.TemplateResponse("user/penilaian.html", {"request": request, "seminar": seminar, "dosen":dosen, "penilaian":penilaian})

@router.get("/penilaian/ubah/{slug}", response_class=HTMLResponse)
def ubahpenilaian(slug: str, request: Request, db: Session = Depends(get_db), user = Depends(user_cookies)):
    nip = user.get("sub")
    dtdosen = db.query(Dosen).filter(Dosen.nip == nip).first()
    seminar = db.query(Seminar).filter(Seminar.slug == slug).first()
    dosen = db.query(SeminarDosen).filter(and_(SeminarDosen.id_dosen == dtdosen.id, SeminarDosen.id_seminar == seminar.id)).first()
    penilaian = db.query(Penilaian).filter(Penilaian.id_seminar_dosen == dosen.id).all()
    return templates.TemplateResponse("user/ubahnilai.html", {"request": request, "seminar": seminar, "dosen":dosen, "penilaian":penilaian})

@router.get("/rekap/{slug}", response_class=HTMLResponse)
def rekapnilai(slug: str, request: Request, db: Session = Depends(get_db), user = Depends(user_cookies)):
    nip = user.get("sub")
    dtdosen = db.query(Dosen).filter(Dosen.nip == nip).first()
    seminar = db.query(Seminar).filter(Seminar.slug == slug).first()
    dosen = db.query(SeminarDosen).filter(and_(SeminarDosen.id_dosen == dtdosen.id, SeminarDosen.id_seminar == seminar.id)).first()
    if not dosen:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Anda tidak memiliki akses ke halaman ini")   
    hasil = db.query(HasilSeminar).filter(HasilSeminar.id_seminar == seminar.id).first()
    return templates.TemplateResponse("user/rekapnilai.html", {"request": request, "seminar": seminar, "hasil": hasil, "dosen":dosen})


@router.put("/batalrekap/{slug}")
def batal_rekap(slug: str, db: Session = Depends(get_db), user = Depends(user_cookies)):
    nip = user.get("sub")
    dtdosen = db.query(Dosen).filter(Dosen.nip == nip).first()
    seminar = db.query(Seminar).filter(Seminar.slug == slug).first()
    dosen = db.query(SeminarDosen).filter(and_(SeminarDosen.id_dosen == dtdosen.id, SeminarDosen.id_seminar == seminar.id)).first()
    if dosen.peran > Peran.sekretaris:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="peran harus ketua/sekretaris")
    if seminar:
        seminar.status = StatusSeminar.terjadwal
        db.commit()
        return {"message": "Rekap nilai berhasil dibatalkan"}

@router.post("/rekap/{slug}")
def postnilaiakhir(slug: str, db: Session = Depends(get_db), user = Depends(user_cookies)):
    nip = user.get("sub")
    dtdosen = db.query(Dosen).filter(Dosen.nip == nip).first()
    seminar = db.query(Seminar).filter(Seminar.slug == slug).first()
    dosen = db.query(SeminarDosen).filter(and_(SeminarDosen.id_dosen == dtdosen.id, SeminarDosen.id_seminar == seminar.id)).first()
    if dosen.peran > Peran.sekretaris:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="peran harus ketua/sekretaris")   
    hasil = db.query(HasilSeminar).filter(HasilSeminar.id_seminar == seminar.id).first()
    nilai = [[], [], [], []]
    if hasil:
        #update nilai
        penilaian_list = db.query(Penilaian).join(SeminarDosen, Penilaian.id_seminar_dosen == SeminarDosen.id).filter(SeminarDosen.id_seminar == seminar.id).all()
        nilai[0] = [u.nilai for u in penilaian_list if u.id_komponen == 1]
        nilai[1] = [u.nilai for u in penilaian_list if u.id_komponen == 2]
        nilai[2] = [u.nilai for u in penilaian_list if u.id_komponen == 3]
        nilai[3] = [u.nilai for u in penilaian_list if u.id_komponen == 4]
        
        penulisan = sum(nilai[0])/len(nilai[0]) 
        materi = sum(nilai[1])/len(nilai[1])
        penyajian = sum(nilai[2])/len(nilai[2])
        pembimbingan = sum(nilai[3])/ (5-nilai[3].count(0))
        nilaiakhir = 0.2 * penulisan + 0.4 * materi + 0.2 * penyajian + 0.2 * pembimbingan
        hasil.nilai_akhir = nilaiakhir
        hasil.grade = get_grade(nilaiakhir)
        seminar.status = StatusSeminar.final
        db.commit()
    else:
        #input pertama kali
        penilaian_list = db.query(Penilaian).join(SeminarDosen, Penilaian.id_seminar_dosen == SeminarDosen.id).filter(SeminarDosen.id_seminar == seminar.id).all()
        nilai[0] = [u.nilai for u in penilaian_list if u.id_komponen == 1]
        nilai[1] = [u.nilai for u in penilaian_list if u.id_komponen == 2]
        nilai[2] = [u.nilai for u in penilaian_list if u.id_komponen == 3]
        nilai[3] = [u.nilai for u in penilaian_list if u.id_komponen == 4]
        
        penulisan = sum(nilai[0])/len(nilai[0]) 
        materi = sum(nilai[1])/len(nilai[1])
        penyajian = sum(nilai[2])/len(nilai[2])
        pembimbingan = sum(nilai[3])/ (5-nilai[3].count(0))
        nilaiakhir = 0.2 * penulisan + 0.4 * materi + 0.2 * penyajian + 0.2 * pembimbingan
        hasil = HasilSeminar(id_seminar=seminar.id, nilai_akhir=nilaiakhir, grade=get_grade(nilaiakhir))
        db.add(hasil)
        seminar.status = StatusSeminar.final
        db.commit()
    return {"message": "Nilai akhir berhasil dihitung"}

@router.get("/riwayatseminar", response_class=HTMLResponse)
def riwayat_seminar(request: Request, db: Session = Depends(get_db), user = Depends(user_cookies)):
    nip = user.get("sub")
    dosen = db.query(Dosen).filter(Dosen.nip == nip).first()
    seminar = db.query(Seminar).join(SeminarDosen, Seminar.id == SeminarDosen.id_seminar).filter(and_(SeminarDosen.id_dosen == dosen.id, Seminar.status == StatusSeminar.selesai)).order_by(Seminar.waktu_seminar.desc()).limit(10).all()
    return templates.TemplateResponse("user/riwayat.html", {"request": request, "data": seminar})