from fastapi import APIRouter, HTTPException, Response, status, Depends, Request, Cookie
from typing import Optional
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from models import get_db, Dosen
from security import user_cookies
from utils import UPLOAD_DIR
import pdfkit
import base64
import os
from io import BytesIO

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def test(request: Request, data =Depends(user_cookies)):
    name = data.get("name")
    return templates.TemplateResponse("test/test.html", {"request": request, "name": name})

@router.get("/badosen", response_class=HTMLResponse)
def badosen(request: Request, data =Depends(user_cookies), db: Session = Depends(get_db)):
    nip = data.get("nip")
    dosen = db.query(Dosen).filter(Dosen.nip == nip).first()
    return templates.TemplateResponse("pdf/ba_dosen.html", {"request": request, "data": dosen})

@router.get("/pdf/badosen")
def badosen_pdf(request: Request, user = Depends(user_cookies), db: Session = Depends(get_db)):
    try:
        # Get dosen data from database
        nip = "199008162025061002"  # Replace with dynamic value if needed
        dosen = db.query(Dosen).filter(Dosen.nip == nip).first()
        if not dosen:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dosen tidak ditemukan")

        # Convert signature image to base64
        signature_src = None
        if dosen.tandatangan:
            signature_path = os.path.join(UPLOAD_DIR, dosen.tandatangan)
            if os.path.exists(signature_path):
                with open(signature_path, "rb") as img_file:
                    img_data = base64.b64encode(img_file.read()).decode()
                    # Determine MIME type from file extension
                    ext = os.path.splitext(dosen.tandatangan)[1].lower()
                    mime_type = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"
                    signature_src = f"data:{mime_type};base64,{img_data}"

        # Render the Jinja2 template to HTML string with data
        template = templates.get_template("pdf/ba_dosen.html")
        html_content = template.render(request=request, data=dosen, signature_src=signature_src)

        # Convert HTML to PDF with optimized options
        options = {
            'page-size': 'A4',
            'margin-top': '0.6in',
            'margin-right': '0.6in',
            'margin-bottom': '0.6in',
            'margin-left': '0.6in',
            "encoding": "UTF-8",
            'enable-local-file-access': None,
            'disable-javascript': None,
            'load-error-handling': "ignore",
            'load-media-error-handling': "ignore",
            'print-media-type': None,
            'dpi': 96,
            'zoom': 1.19,
            'quiet': '',  # Suppress output for faster processing
        }
        pdf_bytes = pdfkit.from_string(html_content, False, options=options)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "inline; filename=berita_acara.pdf"}
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error generating PDF: {str(e)}")

@router.get("/pdf")
def generate_pdf(request: Request, db: Session = Depends(get_db)):
    # Example: Query data from database
    # Replace this with your actual model and query
    # Example: data = db.query(YourModel).all()
    
    # For now, using a sample data structure
    data = {
        "title": "Sample Report",
        "items": [
            {"id": 1, "name": "Item 1", "value": 100},
            {"id": 2, "name": "Item 2", "value": 200},
            {"id": 3, "name": "Item 3", "value": 300},
        ]
    }
    
    # Render the Jinja2 template to HTML string with data
    template = templates.get_template("test/pdf.html")
    html_content = template.render(request=request, data=data)

    # Convert HTML to PDF
    options = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
    }

    pdf_bytes = pdfkit.from_string(html_content, False, options=options)

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "inline; filename=document.pdf"}
    )