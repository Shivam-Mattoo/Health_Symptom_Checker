from typing import List, Dict
import PyPDF2
import pdfplumber
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

class PDFService:
    """Service class for PDF processing and text extraction"""
    
    @staticmethod
    def extract_text_with_ocr(pdf_bytes: bytes) -> str:
        """
        Extract text from image-based PDF using OCR
        
        Args:
            pdf_bytes: PDF file as bytes
        
        Returns:
            Extracted text using OCR
        """
        try:
            import pytesseract
            from pdf2image import convert_from_bytes
            from PIL import Image
            
            logger.info("[PDF SERVICE] Attempting OCR extraction...")
            logger.info("[PDF SERVICE] Converting PDF pages to images...")
            
            # Convert PDF to images
            images = convert_from_bytes(pdf_bytes)
            logger.info(f"[PDF SERVICE] Converted to {len(images)} images")
            
            text_content = []
            for i, image in enumerate(images):
                logger.info(f"[PDF SERVICE] Running OCR on page {i+1}...")
                # Perform OCR on each page
                page_text = pytesseract.image_to_string(image)
                if page_text and page_text.strip():
                    text_content.append(page_text)
                    logger.info(f"[PDF SERVICE] OCR extracted {len(page_text)} chars from page {i+1}")
                else:
                    logger.warning(f"[PDF SERVICE] No text extracted from page {i+1} with OCR")
            
            if text_content:
                combined_text = "\n\n".join(text_content)
                logger.info(f"[PDF SERVICE] OCR extraction complete. Total text: {len(combined_text)} chars")
                return combined_text
            else:
                logger.error("[PDF SERVICE] OCR extraction returned no text")
                return ""
                
        except ImportError as e:
            logger.error(f"[PDF SERVICE] OCR libraries not available: {e}")
            logger.error("[PDF SERVICE] To use OCR, install: pip install pytesseract pdf2image")
            logger.error("[PDF SERVICE] Also install Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
            raise ValueError("OCR libraries not installed. Please install pytesseract and pdf2image, and Tesseract OCR engine.")
        except Exception as e:
            logger.error(f"[PDF SERVICE] OCR extraction error: {str(e)}")
            raise ValueError(f"OCR extraction failed: {str(e)}")
    
    @staticmethod
    def extract_text_from_pdf(pdf_bytes: bytes) -> str:
        """
        Extract text from PDF file
        
        Args:
            pdf_bytes: PDF file as bytes
        
        Returns:
            Extracted text from PDF
        """
        text_content = []
        
        logger.info("[PDF SERVICE] Starting text extraction from PDF")
        logger.info(f"[PDF SERVICE] PDF size: {len(pdf_bytes)} bytes")
        
        # Try using pdfplumber first (better for complex PDFs)
        pdfplumber_success = False
        try:
            logger.info("[PDF SERVICE] Attempting extraction with pdfplumber...")
            with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
                logger.info(f"[PDF SERVICE] PDF opened with pdfplumber. Pages: {len(pdf.pages)}")
                for i, page in enumerate(pdf.pages):
                    logger.info(f"[PDF SERVICE] Extracting text from page {i+1}...")
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text_content.append(page_text)
                        logger.info(f"[PDF SERVICE] Page {i+1} extracted. Text length: {len(page_text)}")
                        pdfplumber_success = True
                    else:
                        logger.warning(f"[PDF SERVICE] Page {i+1} returned no text with pdfplumber")
                logger.info(f"[PDF SERVICE] pdfplumber extraction complete. Total pages with text: {len(text_content)}")
        except ImportError as e:
            logger.warning(f"[PDF SERVICE] pdfplumber not available: {e}")
        except Exception as e:
            logger.warning(f"[PDF SERVICE] Error with pdfplumber: {str(e)}")
        
        # If pdfplumber didn't extract any text, try PyPDF2
        if not pdfplumber_success or len(text_content) == 0:
            logger.info("[PDF SERVICE] pdfplumber didn't extract text, trying PyPDF2 as fallback...")
            try:
                pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
                logger.info(f"[PDF SERVICE] PDF opened with PyPDF2. Pages: {len(pdf_reader.pages)}")
                
                # Clear previous results if pdfplumber failed
                if not pdfplumber_success:
                    text_content = []
                
                for i, page in enumerate(pdf_reader.pages):
                    logger.info(f"[PDF SERVICE] Extracting text from page {i+1} with PyPDF2...")
                    try:
                        page_text = page.extract_text()
                        if page_text and page_text.strip():
                            text_content.append(page_text)
                            logger.info(f"[PDF SERVICE] Page {i+1} extracted with PyPDF2. Text length: {len(page_text)}")
                        else:
                            logger.warning(f"[PDF SERVICE] Page {i+1} returned no text with PyPDF2")
                    except Exception as page_error:
                        logger.warning(f"[PDF SERVICE] Error extracting page {i+1} with PyPDF2: {str(page_error)}")
                
                logger.info(f"[PDF SERVICE] PyPDF2 extraction complete. Total pages with text: {len(text_content)}")
            except ImportError as e:
                logger.error(f"[PDF SERVICE] PyPDF2 not available: {e}")
                if len(text_content) == 0:
                    raise ValueError("Neither pdfplumber nor PyPDF2 is installed. Please install at least one: pip install pdfplumber or pip install PyPDF2")
            except Exception as e2:
                logger.error(f"[PDF SERVICE] Error with PyPDF2: {str(e2)}")
                if len(text_content) == 0:
                    raise ValueError(f"Could not extract text from PDF: {str(e2)}")
        
        if not text_content:
            logger.warning("[PDF SERVICE] No text extracted from any page with either pdfplumber or PyPDF2")
            logger.info("[PDF SERVICE] This appears to be an image-based (scanned) PDF")
            logger.info("[PDF SERVICE] Attempting OCR extraction as fallback...")
            
            try:
                # Try OCR extraction
                ocr_text = PDFService.extract_text_with_ocr(pdf_bytes)
                if ocr_text and ocr_text.strip():
                    logger.info(f"[PDF SERVICE] OCR successful! Extracted {len(ocr_text)} characters")
                    return ocr_text
                else:
                    logger.error("[PDF SERVICE] OCR returned no text")
                    raise ValueError("No text could be extracted from the PDF even with OCR. The PDF might be blank, corrupted, or contain unsupported content.")
            except Exception as ocr_error:
                logger.error(f"[PDF SERVICE] OCR extraction failed: {str(ocr_error)}")
                logger.error("[PDF SERVICE] PDF could not be processed with any method")
                raise ValueError(f"No text could be extracted from the PDF. Standard extraction and OCR both failed. Error: {str(ocr_error)}")
        
        combined_text = "\n\n".join(text_content)
        logger.info(f"[PDF SERVICE] Text extraction complete. Total text length: {len(combined_text)} characters")
        logger.info(f"[PDF SERVICE] First 200 characters: {combined_text[:200]}")
        return combined_text
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into chunks for embedding
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
        
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                if break_point > chunk_size * 0.5:  # Only break if we're past halfway
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return chunks
