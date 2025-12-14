"""
Simple test to identify the exact issue.
"""
import sys

print("Testing imports one by one...")

# Test 1: EasyOCR
print("\n1. Testing EasyOCR...")
try:
    import easyocr
    print("✓ EasyOCR imported successfully")
except Exception as e:
    print(f"✗ EasyOCR failed: {e}")
    sys.exit(1)

# Test 2: pdf2image
print("\n2. Testing pdf2image...")
try:
    from pdf2image import convert_from_bytes
    print("✓ pdf2image imported successfully")
except Exception as e:
    print(f"✗ pdf2image failed: {e}")
    sys.exit(1)

# Test 3: Poppler test
print("\n3. Testing Poppler availability...")
try:
    # Create a minimal PDF for testing
    dummy_pdf = b"%PDF-1.4\n%%EOF"
    convert_from_bytes(dummy_pdf)
    print("✓ Poppler working (unexpected success)")
except Exception as e:
    error_msg = str(e).lower()
    if "poppler" in error_msg or "unable to get page count" in error_msg:
        print("✗ POPPLER NOT INSTALLED!")
        print("\nThis is your problem! Install Poppler:")
        print("1. Run: install_poppler.bat (as administrator)")
        print("2. Or manually download from: https://github.com/oschwartz10612/poppler-windows/releases/")
        print("3. Extract to C:\\poppler")
        print("4. Add C:\\poppler\\Library\\bin to PATH")
        sys.exit(1)
    else:
        print(f"✓ Poppler available (expected error: {str(e)[:50]}...)")

# Test 4: EasyOCR initialization
print("\n4. Testing EasyOCR initialization...")
try:
    print("Initializing EasyOCR (may take time on first run)...")
    reader = easyocr.Reader(['en'], gpu=False, verbose=False)
    print("✓ EasyOCR initialized successfully")
except Exception as e:
    print(f"✗ EasyOCR initialization failed: {e}")
    sys.exit(1)

print("\n✓ All basic tests passed!")
print("The issue might be:")
print("- Large PDF files taking too long to process")
print("- Network issues during first-time model download")
print("- Server timeout settings")