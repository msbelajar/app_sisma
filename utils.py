from babel.dates import format_datetime

UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png"
}
MAX_FILE_SIZE =  0.2 * 1024 * 1024 # 200KB

def format_datetime_id(value):
    return format_datetime(value, locale="id_ID")

def allowed_extension(filename: str) -> bool:
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def validate_magic_bytes(file_bytes: bytes) -> bool:
    """
    Validasi sederhana berdasarkan magic bytes
    JPEG: FF D8 FF
    PNG : 89 50 4E 47
    """
    if file_bytes.startswith(b"\xff\xd8\xff"):
        return True
    if file_bytes.startswith(b"\x89PNG"):
        return True
    return False

def get_grade(nilai:float):
    if nilai >= 81:
        return "A"
    elif nilai >= 66:
        return "B"
    elif nilai >= 51:
        return "C"
    elif nilai >= 36:
        return "D"
    else:
        return "E"