"""
Quick test script to identify PDF processing issues.
Run this to diagnose the problem.
"""
import os
import sys
import time

def test_imports():
    """Test if all required packages are available."""
    print("=== Testing Imports ===")
    
    try:
        import easyocr
        print("✓ EasyOCR imported")
    except ImportError as e:
        print(f"✗ EasyOCR failed: {e}")
        return False
    
    try:
        from pdf2image import convert_from_bytes
        print("✓ pdf2image imported")
    except ImportError as e:
        print(f"✗ pdf2image failed: {e}")
        return False
    
    try:
        import google.generativeai as genai
        print("✓ Google Generative AI imported")
    except ImportError as e:
        print(f"✗ Google Generative AI failed: {e}")
        return False
    
    return True

def test_poppler():
    """Test if Poppler is available."""
    print("\n=== Testing Poppler ===")
    
    try:
        from pdf2image import convert_from_bytes
        # Try to convert a minimal PDF (will fail but show if poppler works)
        dummy_pdf = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n179\n%%EOF"
        convert_from_bytes(dummy_pdf)
    except Exception as e:
        error_msg = str(e).lower()
        if "poppler" in error_msg or "unable to get page count" in error_msg:
            print("✗ Poppler is NOT installed or not in PATH")
            print("\nTo fix:")
            print("1. Download: https://github.com/oschwartz10612/poppler-windows/releases/latest")
            print("2. Extract to C:\\poppler")
            print("3. Add C:\\poppler\\Library\\bin to PATH")
            print("4. Restart terminal/IDE")
            return False
        else:
            print("✓ Poppler seems available (expected error for dummy PDF)")
            return True
    
    print("✓ Poppler is working")
    return True

def test_easyocr_init():
    """Test EasyOCR initialization time."""
    print("\n=== Testing EasyOCR Initialization ===")
    
    try:
        import easyocr
        print("Initializing EasyOCR (this may take time on first run)...")
        start_time = time.time()
        
        reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        
        init_time = time.time() - start_time
        print(f"✓ EasyOCR initialized in {init_time:.1f} seconds")
        
        if init_time > 30:
            print("⚠ Initialization took a long time. This is normal on first run.")
            print("  EasyOCR downloads models (~100MB) on first use.")
        
        return True
        
    except Exception as e:
        print(f"✗ EasyOCR initialization failed: {e}")
        return False

def test_gemini_api():
    """Test Gemini API connection."""
    print("\n=== Testing Gemini API ===")
    
    # Load .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    # Check if API key is set
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # Try reading from .env file directly
        try:
            with open('.env', 'r') as f:
                for line in f:
                    if line.startswith('GEMINI_API_KEY='):
                        api_key = line.split('=', 1)[1].strip()
                        break
        except FileNotFoundError:
            pass
    
    if not api_key:
        print("✗ GEMINI_API_KEY not found in environment or .env file")
        return False
    
    if len(api_key) < 20:
        print("✗ GEMINI_API_KEY seems too short")
        return False
    
    print(f"✓ API key found (length: {len(api_key)})")
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content("Hello, respond with 'API working'")
        
        if "API working" in response.text:
            print("✓ Gemini API is working")
            return True
        else:
            print(f"⚠ Gemini API responded but unexpected content: {response.text}")
            return True
            
    except Exception as e:
        print(f"✗ Gemini API test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("PDF Processing Diagnostic Tool")
    print("=" * 40)
    
    all_good = True
    
    all_good &= test_imports()
    all_good &= test_poppler()
    all_good &= test_easyocr_init()
    all_good &= test_gemini_api()
    
    print("\n" + "=" * 40)
    if all_good:
        print("✓ All tests passed! PDF processing should work.")
        print("\nIf uploads are still slow, it might be:")
        print("- Large PDF files")
        print("- Network issues during model download")
        print("- High CPU usage during OCR processing")
    else:
        print("✗ Some tests failed. Fix the issues above.")
    
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    main()