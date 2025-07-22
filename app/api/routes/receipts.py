"""
Receipt routes for the OCR Receipt Processor API.
Handles receipt retrieval, updates, and management.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...core.database import get_db, Receipt
from ...core.models import ReceiptData
from ...services.extraction_service import ExtractionService

router = APIRouter(prefix="/receipts", tags=["receipts"])

# Initialize services
extraction_service = ExtractionService()

@router.get("/", response_model=List[ReceiptData])
async def get_receipts(db: Session = Depends(get_db)):
    """
    Get all receipts from the database.
    
    Args:
        db: Database session
        
    Returns:
        List of all receipts
    """
    try:
        receipts = db.query(Receipt).all()
        
        receipt_data_list = []
        for receipt in receipts:
            # Parse items properly - ensure it's always a list
            try:
                items = extraction_service.parse_items_json(receipt.items_json)
                if not isinstance(items, list):
                    items = []
            except Exception:
                items = []
            
            receipt_data = ReceiptData(
                id=receipt.id,
                vendor=receipt.vendor,
                transaction_date=receipt.transaction_date.strftime('%Y-%m-%d'),
                amount=receipt.amount,
                currency=receipt.currency,
                category=receipt.category,
                items=items,
                file_name=receipt.filename,
                file_size=0,  # Not stored in DB
                confidence_score=receipt.confidence_score,
                extracted_text=receipt.raw_text,
                upload_timestamp=receipt.created_at.strftime('%Y-%m-%d %H:%M:%S')
            )
            receipt_data_list.append(receipt_data)
        
        return receipt_data_list
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving receipts: {str(e)}"
        )

@router.patch("/{receipt_id}", response_model=ReceiptData)
async def update_receipt(
    receipt_id: int,
    update: dict,
    db: Session = Depends(get_db)
):
    """
    Update a receipt by ID.
    
    Args:
        receipt_id: Receipt ID to update
        update: Dictionary with fields to update
        db: Database session
        
    Returns:
        Updated receipt data
    """
    try:
        receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
        if not receipt:
            raise HTTPException(
                status_code=404,
                detail=f"Receipt with ID {receipt_id} not found"
            )
        
        # Update allowed fields
        allowed_fields = ['vendor', 'amount', 'category', 'currency', 'transaction_date']
        for field, value in update.items():
            if field in allowed_fields and hasattr(receipt, field):
                if field == 'transaction_date':
                    # Parse date string
                    from datetime import datetime
                    try:
                        date_obj = datetime.strptime(value, '%Y-%m-%d')
                        setattr(receipt, field, date_obj)
                    except ValueError:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Invalid date format for {field}. Use YYYY-MM-DD"
                        )
                else:
                    setattr(receipt, field, value)
        
        db.commit()
        db.refresh(receipt)
        
        # Parse items properly - ensure it's always a list
        try:
            items = extraction_service.parse_items_json(receipt.items_json)
            if not isinstance(items, list):
                items = []
        except Exception:
            items = []
        
        # Return updated receipt
        receipt_data = ReceiptData(
            id=receipt.id,
            vendor=receipt.vendor,
            transaction_date=receipt.transaction_date.strftime('%Y-%m-%d'),
            amount=receipt.amount,
            currency=receipt.currency,
            category=receipt.category,
            items=items,
            file_name=receipt.filename,
            file_size=0,
            confidence_score=receipt.confidence_score,
            extracted_text=receipt.raw_text,
            upload_timestamp=receipt.created_at.strftime('%Y-%m-%d %H:%M:%S')
        )
        
        return receipt_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating receipt: {str(e)}"
        )

@router.delete("/{receipt_id}")
async def delete_receipt(
    receipt_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a receipt by ID.
    
    Args:
        receipt_id: Receipt ID to delete
        db: Database session
        
    Returns:
        Success message
    """
    try:
        receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
        if not receipt:
            raise HTTPException(
                status_code=404,
                detail=f"Receipt with ID {receipt_id} not found"
            )
        
        db.delete(receipt)
        db.commit()
        
        return {"message": f"Receipt {receipt_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting receipt: {str(e)}"
        ) 