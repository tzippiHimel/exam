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
        # Parse language setting - support multiple languages separated by + or comma
        lang_setting = settings.OCR_LANGUAGE.strip()
        if '+' in lang_setting:
            languages = [lang.strip() for lang in lang_setting.split('+')]
        elif ',' in lang_setting:
            languages = [lang.strip() for lang in lang_setting.split(',')]
        else:
            languages = [lang_setting]
        
        # Remove empty strings
        languages = [lang for lang in languages if lang]
        
        if not languages:
            languages = ['en']  # Default to English
        
        logger.info(f"Initializing EasyOCR with languages: {languages}")
        logger.info("Note: First-time initialization may take several minutes to download models...")
        try:
            _ocr_reader = easyocr.Reader(languages, gpu=False, verbose=False)
            logger.info("EasyOCR initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {str(e)}")
            raise ValueError(f"OCR initialization failed: {str(e)}. This might be due to network issues or missing dependencies.")
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
        
        # Log image info
        logger.info(f"Processing image: size={image.size}, mode={image.mode}")
        
        # Convert PIL Image to numpy array for EasyOCR
        import numpy as np
        image_array = np.array(image)
        
        # Perform OCR
        logger.info("Running OCR on image...")
        results = reader.readtext(image_array)
        logger.info(f"OCR detected {len(results)} text regions")
        
        # Log confidence scores if available
        if results:
            confidences = [result[2] for result in results if len(result) > 2]
            if confidences:
                avg_confidence = sum(confidences) / len(confidences)
                logger.info(f"Average OCR confidence: {avg_confidence:.2f}")
        
        # Combine all detected text
        text_parts = [result[1] for result in results]
        extracted_text = "\n".join(text_parts)
        
        logger.info(f"Extracted {len(extracted_text)} characters from image")
        
        # Log preview if text is short
        if len(extracted_text) < 200:
            logger.warning(f"Short text extracted. Preview: {extracted_text}")
        else:
            logger.debug(f"Text preview (first 200 chars): {extracted_text[:200]}")
        
        if len(extracted_text.strip()) == 0:
            logger.warning("No text extracted from image. This might indicate:")
            logger.warning("1. Image quality is too low")
            logger.warning("2. Text is too small or unclear")
            logger.warning("3. OCR language setting doesn't match the text language")
            logger.warning(f"4. Current OCR language: {settings.OCR_LANGUAGE}")
        
        return extracted_text.strip()
        
    except Exception as e:
        logger.error(f"Error extracting text from image: {str(e)}", exc_info=True)
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
        # Ensure Poppler is in PATH for this process
        import os
        poppler_path = r"C:\poppler-25.12.0\Library\bin"
        if poppler_path not in os.environ.get('PATH', ''):
            os.environ['PATH'] = os.environ.get('PATH', '') + ';' + poppler_path
            logger.info(f"Added Poppler to PATH: {poppler_path}")
        logger.info(f"Converting PDF to images (PDF size: {len(pdf_bytes)} bytes)")
        
        # Check PDF size and adjust DPI accordingly
        pdf_size_mb = len(pdf_bytes) / (1024 * 1024)
        if pdf_size_mb > 2:
            dpi = 100  # Much lower DPI for faster processing
            logger.info(f"PDF ({pdf_size_mb:.1f}MB), using DPI=100 for speed")
        else:
            dpi = 150  # Lower DPI for better speed
            logger.info(f"PDF size: {pdf_size_mb:.1f}MB, using DPI=150")
        
        # Convert PDF to images with timeout protection
        logger.info("Starting PDF conversion...")
        images = convert_from_bytes(pdf_bytes, dpi=dpi, first_page=1, last_page=3)  # Limit to first 3 pages for speed
        logger.info(f"PDF converted to {len(images)} page(s)")
        
        if len(images) == 0:
            raise ValueError("PDF conversion resulted in 0 pages. The PDF might be corrupted or empty.")
        
        all_text = []
        for i, image in enumerate(images):
            logger.info(f"Processing PDF page {i + 1}/{len(images)} (size: {image.size})")
            
            # Optimize image for OCR
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize image for faster OCR
            max_width = 1200
            if image.width > max_width:
                ratio = max_width / image.width
                new_height = int(image.height * ratio)
                image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)
                logger.info(f"Resized image to {image.size} for faster OCR")
            
            # Convert PIL Image to bytes for OCR with optimized quality
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='PNG', optimize=True, quality=75)
            img_bytes.seek(0)
            
            try:
                page_text = extract_text_from_image(img_bytes.getvalue())
                all_text.append(page_text)
                logger.info(f"Page {i + 1}: Extracted {len(page_text)} characters")
                
                # Early exit if we have enough text (optimization)
                total_chars = sum(len(text) for text in all_text)
                if total_chars > 1000 and i >= 1:  # Stop after 2 pages if we have enough text
                    logger.info(f"Early exit: extracted {total_chars} characters from {i+1} pages")
                    break
                    
            except Exception as page_error:
                logger.error(f"Error processing PDF page {i + 1}: {str(page_error)}")
                all_text.append(f"[Error extracting text from page {i + 1}]")
        
        combined_text = "\n\n".join(all_text)
        logger.info(f"Total extracted from PDF: {len(combined_text)} characters")
        
        if len(combined_text.strip()) < 10:
            raise ValueError("PDF processing extracted very little text. The PDF might be image-based or corrupted. Try converting to images first.")
        
        return combined_text.strip()
        
    except ValueError as e:
        # Re-raise ValueError as-is
        logger.error(f"PDF processing error: {str(e)}")
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error extracting text from PDF: {error_msg}", exc_info=True)
        
        # Check if it's a poppler error
        if "poppler" in error_msg.lower() or "Unable to get page count" in error_msg or "poppler" in str(e).lower() or "pdf2image" in error_msg.lower():
            detailed_error = (
                "PDF processing failed: Poppler is not installed or not in PATH.\n\n"
                "QUICK FIX - Download and install Poppler:\n"
                "1. Download: https://github.com/oschwartz10612/poppler-windows/releases/latest\n"
                "2. Extract to C:\\poppler\n"
                "3. Add to PATH: C:\\poppler\\Library\\bin\n"
                "4. Restart the server\n\n"
                "OR use the batch file: התקנת_Poppler_Windows.md\n\n"
                "Alternative solutions:\n"
                "- Convert PDF to images (.png, .jpg) and upload those instead\n"
                "- Use a text file (.txt) if you have the text version\n"
                "- Use Docker (poppler is pre-installed in the Docker image)"
            )
        else:
            detailed_error = (
                f"PDF processing failed: {error_msg}\n\n"
                "Please try:\n"
                "1. Converting PDF to images (.png, .jpg) and upload those\n"
                "2. Using a text file (.txt) if available\n"
                "3. Ensuring the PDF contains readable text (not just images)\n"
                "4. Installing Poppler if not already installed"
            )
        
        raise ValueError(detailed_error)


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

