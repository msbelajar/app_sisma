from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from models import get_db
import pdfkit
from io import BytesIO

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def test(request: Request):
    return templates.TemplateResponse("test/test.html", {"request": request})

@router.get("/pdf")
def generate_pdf(request: Request):
    # Render the Jinja2 template to HTML string
    template = templates.get_template("test/pdf.html")
    html_content = template.render(request=request)

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