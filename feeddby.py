from models import SessionLocal, Dosen, Mahasiswa
from schemas import Role
import csv
from security import genpass

db = SessionLocal()

def feeddbmhs():
    with open('mhs.csv', 'r', newline='', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file, delimiter=";")
        for row in reader:
            # print(row)
            try:
                data = Mahasiswa(nim=row['nim'], nama_mahasiswa=row['nama'])
                db.add(data)
                db.commit()
            except:
                print(f"error {row['nama']}")

def datadosen():
    with open('dosen.csv', 'r', newline='', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file, delimiter=";")
        for row in reader:
            # print(row)
            try:
                data = Dosen(nip=row['nip'], nama_dosen=row['nama'], password=genpass('112233'))
                db.add(data)
                db.commit()
            except:
                print(f"error {row['nama']}")

# def getdata(nim):
#     cc = db.query(User).filter(User.username == nim).first()
#     return cc

def removealldosen():
    db.query(Dosen).delete()
    db.commit()
    db.close()

# def adddosen():
#     data = User(username='199008162025061002', nama='Muhammad Sadno, S.Si., M.Si.', password=genpass('OnoimaN'), isactive=True, role=Role.dosen)
#     db.add(data)
#     db.commit()
#     db.close()

def addadmin():
    # data = User(username='hanif', nama='Admin', password=genpass('163064'), isactive=True, role=Role.admin)
    data = Dosen(nip='00112233', nama_dosen='Admin SISMA', email='ono.sadno@gmail.com', password=genpass('112233'), role=Role.admin)
    db.add(data)
    db.commit()
    db.close()

if __name__ == "__main__":
    feeddbmhs()
    addadmin()
    datadosen()