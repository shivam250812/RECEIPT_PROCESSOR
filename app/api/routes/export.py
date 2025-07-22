"""
Export routes for the OCR Receipt Processor API.
Handles data export in various formats.
"""

import csv
import io
import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ...core.database import get_db, Receipt
from ...core.models import ReceiptData
from ...services.extraction_service import ExtractionService

router = APIRouter(prefix="/export", tags=["export"])

# Initialize services
extraction_service = ExtractionService()

@router.get("/csv")
async def export_csv(db: Session = Depends(get_db)):
    """
    Export all receipt data as CSV.
    
    Args:
        db: Database session
        
    Returns:
        CSV file download
    """
    try:
        # Get all receipts
        receipts = db.query(Receipt).all()
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'id', 'vendor', 'transaction_date', 'amount', 'currency',
            'category', 'confidence_score', 'file_name', 'created_at'
        ])
        
        # Write data
        for receipt in receipts:
            writer.writerow([
                receipt.id,
                receipt.vendor,
                receipt.transaction_date.strftime('%Y-%m-%d'),
                receipt.amount,
                receipt.currency,
                receipt.category,
                receipt.confidence_score,
                receipt.filename,
                receipt.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        # Create response
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=receipts.csv"}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"CSV export failed: {str(e)}"
        )

@router.get("/json")
async def export_json(db: Session = Depends(get_db)):
    """
    Export all receipt data as JSON.
    
    Args:
        db: Database session
        
    Returns:
        JSON file download
    """
    try:
        # Get all receipts
        receipts = db.query(Receipt).all()
        
        # Convert to JSON format
        receipt_data_list = []
        for receipt in receipts:
            receipt_data = ReceiptData(
                id=receipt.id,
                vendor=receipt.vendor,
                transaction_date=receipt.transaction_date.strftime('%Y-%m-%d'),
                amount=receipt.amount,
                currency=receipt.currency,
                category=receipt.category,
                items=extraction_service.parse_items_json(receipt.items_json),
                file_name=receipt.filename,
                file_size=0,
                confidence_score=receipt.confidence_score,
                extracted_text=receipt.raw_text,
                upload_timestamp=receipt.created_at.strftime('%Y-%m-%d %H:%M:%S')
            )
            receipt_data_list.append(receipt_data.dict())
        
        # Create JSON content
        json_content = json.dumps(receipt_data_list, indent=2, default=str)
        
        # Create response
        return StreamingResponse(
            io.BytesIO(json_content.encode('utf-8')),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=receipts.json"}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"JSON export failed: {str(e)}"
        ) 