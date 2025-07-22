"""
Upload routes for the OCR Receipt Processor API.
Handles file uploads, OCR processing, and data extraction.
"""

import os
import time
import uuid
from typing import List
from datetime import datetime

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session

from ...core.database import get_db, Receipt
from ...core.models import FileUploadResponse, ReceiptData
from ...services.ocr_service import OCRService
from ...services.extraction_service import ExtractionService
from ...core.config import settings

router = APIRouter(prefix="/upload", tags=["upload"])

# Initialize services
ocr_service = OCRService()
extraction_service = ExtractionService()

@router.post("/", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and process a receipt file.
    
    Args:
        file: Uploaded file (image, PDF, or text)
        db: Database session
        
    Returns:
        FileUploadResponse with extracted data
    """
    start_time = time.time()
    
    # Validate file format
    file_extension = os.path.splitext(file.filename)[1].lower()
    if not ocr_service.validate_file_format(file_extension):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Supported formats: {ocr_service.get_supported_formats()}"
        )
    
    # Validate file size
    if file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    try:
        # Create unique filename
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Extract text using OCR
        extracted_text, ocr_confidence = ocr_service.extract_text_from_file(
            file_path, file_extension
        )
        
        if not extracted_text:
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from file. Please ensure the file contains readable text."
            )
        
        # Extract structured data
        extracted_data = extraction_service.parse_receipt_text(
            extracted_text, file.filename, file.size
        )
        
        # Create database record
        db_receipt = Receipt(
            filename=file.filename,
            file_type=file_extension,
            vendor=extracted_data['vendor'],
            transaction_date=datetime.strptime(extracted_data['transaction_date'], '%Y-%m-%d'),
            amount=extracted_data['amount'],
            category=extracted_data['category'],
            currency=extracted_data.get('currency', 'USD'),
            raw_text=extracted_data['extracted_text'],
            confidence_score=extracted_data['confidence_score'],
            items_json=str(extracted_data['items'])  # Store as JSON string
        )
        
        db.add(db_receipt)
        db.commit()
        db.refresh(db_receipt)
        
        # Create response data
        receipt_data = ReceiptData(
            id=db_receipt.id,
            vendor=db_receipt.vendor,
            transaction_date=db_receipt.transaction_date.strftime('%Y-%m-%d'),
            amount=db_receipt.amount,
            currency=db_receipt.currency,
            category=db_receipt.category,
            items=extracted_data['items'],
            file_name=db_receipt.filename,
            file_size=file.size,
            confidence_score=db_receipt.confidence_score,
            extracted_text=db_receipt.raw_text,
            upload_timestamp=db_receipt.created_at.strftime('%Y-%m-%d %H:%M:%S')
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        return FileUploadResponse(
            message=f"Receipt processed successfully in {processing_time:.2f}ms",
            receipt_id=db_receipt.id,
            extracted_data=receipt_data
        )
        
    except Exception as e:
        # Clean up uploaded file on error
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )
    
    finally:
        # Clean up uploaded file
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)

@router.get("/supported-formats")
async def get_supported_formats():
    """
    Get list of supported file formats.
    
    Returns:
        List of supported file extensions
    """
    return {
        "supported_formats": ocr_service.get_supported_formats(),
        "max_file_size_mb": settings.MAX_FILE_SIZE / (1024 * 1024)
    } 