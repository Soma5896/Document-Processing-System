# Intelligent Document Processing System

This project is an AI-powered system that extracts structured information from unstructured documents such as invoices, resumes, and legal contracts using OCR, NLP, and machine learning.

---

## 🚀 Features

- 📄 **OCR**: Text extraction from images using Tesseract and OpenCV
- 🧠 **Classification**: Categorize documents into `invoice`, `resume`, `contract`, etc.
- 🔍 **Information Extraction**:
  - Invoice fields: Vendor, Customer, Invoice Number, Line Items, Dates
  - Resume fields: Name, Email, Phone, Skills, Companies, Education
  - Contract fields: Parties, Dates, Amounts, Terms
- 🌐 **Multi-format Support**: `.pdf`, `.docx`, `.txt`, `.jpg`, `.png`
- 📦 **FastAPI Backend**: Exposes `/process/` endpoint for document upload and processing

---

## 🧱 Project Structure

```
project-root/
│
├── app/
│   ├── services/
│   │   ├── ocr_service.py
│   │   ├── classifier.py
│   │   ├── information_extractor.py
│   ├── uploads/
│   └── api.py
│
├── main.py
└── README.md
```

---

## 🛠️ Installation

1. Clone this repo  
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Install [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)

---

## 🧪 Run the App

```bash
uvicorn main:app --reload
```

Then open: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📥 Upload Example

```bash
curl -X POST -F "file=@example_invoice.pdf" http://127.0.0.1:8000/process/
```

---

## 📚 Sample Outputs

```json
{
  "category": "invoice",
  "extracted_text": "...",
  "entities": {
    "vendor_name": "Acme Corp",
    "invoice_number": "INV-1234",
    ...
  }
}
```

---

## 📌 Notes

- Be sure to include good quality images for OCR
- Extendable for more document types (e.g. medical, forms, ID cards)
