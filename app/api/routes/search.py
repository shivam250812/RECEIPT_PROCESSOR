"""
Search routes for the OCR Receipt Processor API.
Handles advanced search operations using various algorithms.
"""

import time
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...core.database import get_db, Receipt
from ...core.models import SearchQuery, SearchResponse, ReceiptData
from ...algorithms.search_algorithms import SearchAlgorithms
from ...services.extraction_service import ExtractionService

router = APIRouter(prefix="/search", tags=["search"])

# Initialize services
search_algorithms = SearchAlgorithms()
extraction_service = ExtractionService()

@router.post("/", response_model=SearchResponse)
async def search_receipts(
    search_query: SearchQuery,
    db: Session = Depends(get_db)
):
    """
    Search receipts using various algorithms.
    
    Args:
        search_query: Search parameters
        db: Database session
        
    Returns:
        SearchResponse with results and metadata
    """
    start_time = time.time()
    
    try:
        # Get all receipts from database
        db_receipts = db.query(Receipt).all()
        
        # Convert to list of dictionaries for algorithm processing
        receipts = []
        for receipt in db_receipts:
            receipt_dict = {
                'id': receipt.id,
                'vendor': receipt.vendor,
                'transaction_date': receipt.transaction_date.strftime('%Y-%m-%d'),
                'amount': receipt.amount,
                'currency': receipt.currency,
                'category': receipt.category,
                'confidence_score': receipt.confidence_score,
                'file_name': receipt.filename,
                'items': extraction_service.parse_items_json(receipt.items_json),
                'extracted_text': receipt.raw_text,
                'upload_timestamp': receipt.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            receipts.append(receipt_dict)
        
        # Perform search based on algorithm
        if search_query.algorithm == 'range':
            # Convert min_value and max_value to float if not None
            min_value = float(search_query.min_value) if search_query.min_value is not None else None
            max_value = float(search_query.max_value) if search_query.max_value is not None else None
            results = search_algorithms._range_search(
                receipts,
                min_value=min_value,
                max_value=max_value,
                field=search_query.field
            )
        elif search_query.algorithm == 'pattern':
            # Handle pattern search with regex
            results = search_algorithms.search(
                receipts,
                query=search_query.query,
                algorithm=search_query.algorithm,
                field=search_query.field,
                pattern=search_query.pattern
            )
        elif search_query.algorithm == 'fuzzy':
            # Handle fuzzy search with threshold
            results = search_algorithms.search(
                receipts,
                query=search_query.query,
                algorithm=search_query.algorithm,
                field=search_query.field,
                threshold=search_query.threshold
            )
        else:
            # Handle standard search
            results = search_algorithms.search(
                receipts,
                query=search_query.query,
                algorithm=search_query.algorithm,
                field=search_query.field
            )
        
        # Convert results to ReceiptData models
        receipt_data_list = []
        for result in results:
            receipt_data = ReceiptData(
                id=result['id'],
                vendor=result['vendor'],
                transaction_date=result['transaction_date'],
                amount=result['amount'],
                currency=result['currency'],
                category=result['category'],
                items=result['items'],
                file_name=result['file_name'],
                file_size=0,  # Not stored in DB
                confidence_score=result['confidence_score'],
                extracted_text=result['extracted_text'],
                upload_timestamp=result['upload_timestamp']
            )
            receipt_data_list.append(receipt_data)
        
        execution_time = (time.time() - start_time) * 1000
        
        return SearchResponse(
            results=receipt_data_list,
            total_count=len(receipt_data_list),
            algorithm_used=search_query.algorithm,
            execution_time_ms=execution_time,
            query_info={
                'query': search_query.query,
                'field': search_query.field,
                'threshold': search_query.threshold,
                'min_value': search_query.min_value,
                'max_value': search_query.max_value,
                'pattern': search_query.pattern
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        ) 