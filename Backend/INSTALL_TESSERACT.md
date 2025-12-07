# Installing Tesseract OCR for Windows

## What is Tesseract?
Tesseract is an OCR (Optical Character Recognition) engine that reads text from images. It's required for processing scanned/image-based PDFs.

## Installation Steps

### Option 1: Using Chocolatey (Recommended)
If you have Chocolatey package manager installed:
```powershell
choco install tesseract
```

### Option 2: Manual Installation (Most Common)

1. **Download Tesseract Installer**
   - Go to: https://github.com/UB-Mannheim/tesseract/wiki
   - Download the latest installer (e.g., `tesseract-ocr-w64-setup-5.3.3.20231005.exe`)
   - Or direct link: https://digi.bib.uni-mannheim.de/tesseract/

2. **Run the Installer**
   - Run the downloaded `.exe` file
   - Default installation path: `C:\Program Files\Tesseract-OCR`
   - **Important:** During installation, make sure to select "Add to PATH" option
   - Or note the installation path to add manually

3. **Add Tesseract to PATH (if not done automatically)**
   - Open System Environment Variables
   - Edit the `PATH` variable
   - Add: `C:\Program Files\Tesseract-OCR` (or your installation path)
   - Click OK

4. **Verify Installation**
   ```powershell
   tesseract --version
   ```
   You should see output like: `tesseract 5.3.3`

### Option 3: Using Scoop Package Manager
If you have Scoop installed:
```powershell
scoop install tesseract
```

## After Installation

1. **Restart your PowerShell terminal**
2. **Verify Tesseract is accessible:**
   ```powershell
   tesseract --version
   ```

3. **If tesseract is not found**, you may need to configure pytesseract:
   
   Create or edit `config.py` in your Backend folder and add:
   ```python
   # Tesseract configuration (only if not in PATH)
   TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

   Then in your `pdf_service.py`, add at the top:
   ```python
   import pytesseract
   from config import Config
   
   # Only if Tesseract is not in PATH
   if hasattr(Config, 'TESSERACT_CMD'):
       pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_CMD
   ```

## Testing OCR

After installation, restart your FastAPI server and try uploading your PDF again!

## Troubleshooting

### Error: "tesseract is not installed or it's not in your PATH"
- Make sure Tesseract is installed
- Verify PATH includes Tesseract installation directory
- Restart your terminal/IDE after installation

### Error: "Failed to execute tesseract"
- Check if Tesseract is accessible: `tesseract --version`
- Try the manual configuration method above

### Slow OCR Processing
- OCR is slower than text extraction (normal for scanned PDFs)
- Large PDFs may take 10-30 seconds
- Consider adding progress indicators in production

## Alternative: Use Text-Based PDFs
If possible, ask for PDFs with selectable text instead of scanned images for faster processing.
