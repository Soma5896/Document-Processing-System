# Document-Processing-System

doc-project/
│
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI app entry point
│   ├── api.py                 # Unified API: OCR + text extraction + classification
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ocr_service.py     # (Optional, if OCR is separated here)
│   │   ├── classifier.py      # TF-IDF + SVM classifier logic
│   │   └── document_classifier.pkl  # Trained classifier model
│   └── uploads/               # Stores uploaded files
│
├── train_classifier.py        # Script to train classifier & generate .pkl
├── requirements.txt           # Dependencies
├── README.md                  # (optional) Project documentation





for entire project:

doc-project/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── api.py                  # All API endpoints
│   │
│   ├── services/               # Core logic components
│   │   ├── __init__.py
│   │   ├── ocr_service.py      # Image OCR logic
│   │   ├── classifier.py       # Document Classification logic
│   │   └── text_extractor.py   # Extract text from PDFs, TXT, DOCX
│   │
│   ├── models/                 # (Optional for DB models in future)
│   │   ├── __init__.py
│   │   └── document_model.py
│   │
│   ├── uploads/                # Folder to store uploaded files
│
├── models/                     # Pre-trained ML models
│   └── document_classifier.pkl # Trained SVM classifier
│
├── train_classifier.py         # Script to train & save the classifier
│
├── requirements.txt            # Project dependencies
├── README.md                   # Project documentation
└── .gitignore                  # To exclude uploads, .pkl, __pycache__

