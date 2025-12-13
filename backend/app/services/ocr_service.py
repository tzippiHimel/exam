"""
OCR service for extracting text from images and PDFs.
"""
import io
import logging
from typing import Optional
from PIL import Image
import easyocr
from pdf2image import convert_from_bytes
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize EasyOCR reader (lazy loading)
_ocr_reader: Optional[easyocr.Reader] = None


def get_ocr_reader() -> easyocr.Reader:
    """Get or initialize OCR reader."""
    global _ocr_reader
    if _ocr_reader is None:
        logger.info(f"Initializing EasyOCR with language: {settings.OCR_LANGUAGE}")
        _ocr_reader = easyocr.Reader([settings.OCR_LANGUAGE], gpu=False)
    return _ocr_reader


def extract_text_from_image(image_bytes: bytes) -> str:
    """
    Extract text from image bytes using EasyOCR.
    
    Args:
        image_bytes: Image file bytes
        
    Returns:
        Extracted text string
    """
    try:
        reader = get_ocr_reader()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert PIL Image to numpy array for EasyOCR
        import numpy as np
        image_array = np.array(image)
        
        # Perform OCR
        results = reader.readtext(image_array)
        
        # Combine all detected text
        text_parts = [result[1] for result in results]
        extracted_text = "\n".join(text_parts)
        
        logger.info(f"Extracted {len(extracted_text)} characters from image")
        return extracted_text.strip()
        
    except Exception as e:
        logger.error(f"Error extracting text from image: {str(e)}")
        raise ValueError(f"OCR extraction failed: {str(e)}")


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract text from PDF by converting to images and using OCR.
    
    Args:
        pdf_bytes: PDF file bytes
        
    Returns:
        Extracted text string
    """
    try:
        # Convert PDF to images
        images = convert_from_bytes(pdf_bytes)
        
        all_text = []
        for i, image in enumerate(images):
            logger.info(f"Processing PDF page {i + 1}/{len(images)}")
            # Convert PIL Image to bytes for OCR
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            page_text = extract_text_from_image(img_bytes.getvalue())
            all_text.append(page_text)
        
        combined_text = "\n\n".join(all_text)
        logger.info(f"Extracted {len(combined_text)} characters from PDF")
        return combined_text.strip()
        
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise ValueError(f"PDF OCR extraction failed: {str(e)}")


def extract_text_from_file(file_bytes: bytes, file_extension: str) -> str:
    """
    Extract text from file based on extension.
    
    Args:
        file_bytes: File bytes
        file_extension: File extension (e.g., '.pdf', '.png')
        
    Returns:
        Extracted text string
    """
    file_extension = file_extension.lower()
    
    if file_extension == '.pdf':
        return extract_text_from_pdf(file_bytes)
    elif file_extension in ['.png', '.jpg', '.jpeg']:
        return extract_text_from_image(file_bytes)
    elif file_extension == '.txt':
        # Direct text file
        try:
            return file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            return file_bytes.decode('latin-1')
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

