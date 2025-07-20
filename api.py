from fastapi import APIRouter, UploadFile, File
import os
import cv2
import pytesseract
from docx import Document
import fitz  # PyMuPDF
from app.services.classifier import DocumentClassifier

router = APIRouter()
UPLOAD_FOLDER = "app/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

classifier = DocumentClassifier()
classifier.load_model()

class OCRService:
    def __init__(self):
        self.config = '--oem 3 --psm 6'

    def preprocess_image(self, image_path):
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        denoised = cv2.fastNlMeansDenoising(gray)
        return denoised

    def extract_text(self, image_path):
        processed_image = self.preprocess_image(image_path)
        return pytesseract.image_to_string(processed_image, config=self.config)

ocr_service = OCRService()

def extract_text_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as pdf:
        for page in pdf:
            text += page.get_text()
    return text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

@router.post("/process/")
async def process_and_classify(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Step 1: Extract Text
    text = ""
    if file.content_type.startswith("image/"):
        text = ocr_service.extract_text(file_path)
        source = "OCR from image"
    elif file.filename.lower().endswith(".txt"):
        text = extract_text_from_txt(file_path)
        source = "TXT file"
    elif file.filename.lower().endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
        source = "PDF file"
    elif file.filename.lower().endswith(".docx"):
        text = extract_text_from_docx(file_path)
        source = "DOCX file"
    else:
        return {"error": "Unsupported file format for text extraction."}

    if not text.strip():
        return {"error": "No text could be extracted from the file."}

    # Step 2: Classify Text
    classification = classifier.classify(text)

    return {
        "message": f"Text extracted using {source}",
        "extracted_text": text,
        "classification": classification
    }
