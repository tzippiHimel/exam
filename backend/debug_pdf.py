"""
Debug script to test PDF processing step by step.
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ocr_service import extract_text_from_pdf
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)

def test_pdf_processing():
    """Test PDF processing with a sample file."""
    print("Testing PDF processing...")
    
    # Test if poppler is available
    try:
        from pdf2image import convert_from_path
        print("✓ pdf2image imported successfully")
    except ImportError as e:
        print(f"✗ pdf2image import failed: {e}")
        return
    
    # Test if EasyOCR is available
    try:
        import easyocr
        print("✓ EasyOCR imported successfully")
    except ImportError as e:
        print(f"✗ EasyOCR import failed: {e}")
        return
    
    # Test poppler availability
    try:
        # Try to convert a dummy PDF (this will fail but show if poppler works)
        convert_from_path("dummy.pdf")
    except Exception as e:
        error_msg = str(e).lower()
        if "poppler" in error_msg or "unable to get page count" in error_msg:
            print("✗ Poppler is not installed or not in PATH")
            print("Install Poppler:")
            print("1. Download from: https://github.com/oschwartz10612/poppler-windows/releases/")
            print("2. Extract to C:\\poppler")
            print("3. Add C:\\poppler\\Library\\bin to PATH")
            return
        else:
            print("✓ Poppler seems to be available (expected error for dummy file)")
    
    # Test EasyOCR initialization
    try:
        print("Initializing EasyOCR (this may take time on first run)...")
        reader = easyocr.Reader(['en'], gpu=False)
        print("✓ EasyOCR initialized successfully")
    except Exception as e:
        print(f"✗ EasyOCR initialization failed: {e}")
        return
    
    print("\nAll components seem to be working!")
    print("If PDF upload is still slow, it might be:")
    print("1. Large PDF file size")
    print("2. First-time EasyOCR model download")
    print("3. High DPI conversion taking time")

if __name__ == "__main__":
    test_pdf_processing()