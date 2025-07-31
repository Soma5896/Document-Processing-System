import cv2 # OpenCV for image processing
import pytesseract # Tesseract for OCR
import numpy as np 
# from PIL import Image  # not used, can be removed

class OCRService:
    def __init__(self):
        self.config = '--oem 3 --psm 6' # Tesseract configuration for OCR 
    '''
     --oem → OCR Engine Mode
     --psm → Page Segmentation 
     psm 6 is suitable for a single uniform block of text
     psm 3 is for fully automatic page segmentation, but psm 6 is often better for structured documents like invoices or resumes.
     psm 11 is for sparse text, which is not suitable for structured documents.
    '''

    def preprocess_image(self, image_path):
        image = cv2.imread(image_path) 
        if image is None:
            raise ValueError(f"Cannot read image at {image_path}") # Check if image is read correctly
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # Convert to grayscale
        denoised = cv2.fastNlMeansDenoising(gray) # Denoise the image
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)) #apply CLAHE for contrast enhancement
        enhanced = clahe.apply(denoised) # Contrast Limited Adaptive Histogram Equalization
        return enhanced

    def extract_text(self, image_path):
        processed_image = self.preprocess_image(image_path) # Process the image before OCR
        data = pytesseract.image_to_data(processed_image, config=self.config, output_type=pytesseract.Output.DICT)
        confident_text = []
        for i, conf in enumerate(data['conf']):
            try:
                if float(conf) > 60:
                    confident_text.append(data['text'][i])
            except ValueError:
                continue
        return ' '.join(confident_text) # Extract text with confidence filtering


