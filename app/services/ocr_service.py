"""
OCR Service for text extraction from images and documents.
Handles multiple file formats and provides confidence scoring.
"""

import os
import re
from typing import Optional, Tuple
from pathlib import Path

import pytesseract
from PIL import Image
import pdf2image
import io
from PyPDF2 import PdfReader

from ..core.config import settings

class OCRService:
    """Service for OCR text extraction and processing."""
    
    def __init__(self):
        """Initialize OCR service with Tesseract configuration."""
        if settings.TESSERACT_PATH:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_PATH
    
    def extract_text_from_image(self, image_path: str) -> Tuple[str, float]:
        """
        Extract text from image using OCR.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        try:
            image = Image.open(image_path)
            
            # Extract text with confidence
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Combine text with confidence scores
            text_parts = []
            total_confidence = 0
            valid_words = 0
            
            for i, conf in enumerate(data['conf']):
                if conf > 0:  # Only include words with confidence > 0
                    text_parts.append(data['text'][i])
                    total_confidence += conf
                    valid_words += 1
            
            extracted_text = ' '.join(text_parts).strip()
            confidence_score = total_confidence / max(valid_words, 1) / 100.0
            
            return extracted_text, confidence_score
            
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            return "", 0.0
    
    def extract_text_from_pdf(self, pdf_path: str) -> Tuple[str, float]:
        """
        Extract text from PDF using direct extraction and OCR fallback.
        Args:
            pdf_path: Path to the PDF file
        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        try:
            # First, try direct text extraction
            text = ""
            try:
                with open(pdf_path, 'rb') as f:
                    reader = PdfReader(f)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            except Exception as e:
                print(f"Direct PDF text extraction failed: {e}")
            if text.strip():
                # If text was found, return it with high confidence
                return text.strip(), 0.95
            # If no text, fall back to OCR
            images = pdf2image.convert_from_path(pdf_path)
            all_text = []
            total_confidence = 0
            page_count = 0
            for image in images:
                # Use in-memory image for OCR
                data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
                text_parts = []
                total_page_conf = 0
                valid_words = 0
                for i, conf in enumerate(data['conf']):
                    if conf > 0:
                        text_parts.append(data['text'][i])
                        total_page_conf += conf
                        valid_words += 1
                page_text = ' '.join(text_parts).strip()
                if page_text:
                    all_text.append(page_text)
                    if valid_words > 0:
                        total_confidence += total_page_conf / valid_words / 100.0
                    else:
                        total_confidence += 0
                    page_count += 1
            combined_text = '\n'.join(all_text).strip()
            avg_confidence = total_confidence / max(page_count, 1)
            return combined_text, avg_confidence
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return "", 0.0
    
    def extract_text_from_text_file(self, file_path: str) -> Tuple[str, float]:
        """
        Extract text from plain text files.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read().strip()
            
            # Simple confidence based on text length and content
            confidence = min(len(text) / 1000.0, 1.0)  # Higher confidence for longer text
            
            return text, confidence
            
        except Exception as e:
            print(f"Error reading text file: {e}")
            return "", 0.0
    
    def extract_text_from_file(self, file_path: str, file_extension: str) -> Tuple[str, float]:
        """
        Extract text based on file type.
        
        Args:
            file_path: Path to the file
            file_extension: File extension (with dot)
            
        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        file_extension = file_extension.lower()
        
        if file_extension in settings.SUPPORTED_IMAGE_FORMATS:
            return self.extract_text_from_image(file_path)
        elif file_extension in settings.SUPPORTED_DOCUMENT_FORMATS:
            return self.extract_text_from_pdf(file_path)
        elif file_extension in settings.SUPPORTED_TEXT_FORMATS:
            return self.extract_text_from_text_file(file_path)
        else:
            print(f"Unsupported file format: {file_extension}")
            return "", 0.0
    
    def validate_file_format(self, file_extension: str) -> bool:
        """
        Validate if file format is supported.
        
        Args:
            file_extension: File extension (with dot)
            
        Returns:
            True if format is supported, False otherwise
        """
        file_extension = file_extension.lower()
        supported_formats = (
            settings.SUPPORTED_IMAGE_FORMATS +
            settings.SUPPORTED_DOCUMENT_FORMATS +
            settings.SUPPORTED_TEXT_FORMATS
        )
        return file_extension in supported_formats
    
    def get_supported_formats(self) -> list:
        """
        Get list of supported file formats.
        
        Returns:
            List of supported file extensions
        """
        return (
            settings.SUPPORTED_IMAGE_FORMATS +
            settings.SUPPORTED_DOCUMENT_FORMATS +
            settings.SUPPORTED_TEXT_FORMATS
        ) 