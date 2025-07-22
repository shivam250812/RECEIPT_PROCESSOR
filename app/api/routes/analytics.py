"""
Analytics routes for the OCR Receipt Processor API.
Handles sorting, aggregation, and statistical operations.
"""

import time
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from ...core.database import get_db, Receipt
from ...core.models import (
    SortOptions, SortResponse, AggregationRequest, AggregationResponse,
    StatisticsResponse, ReceiptData, AlgorithmInfoResponse
)
from ...algorithms.search_algorithms import SearchAlgorithms
from ...algorithms.aggregation_algorithms import AggregationAlgorithms
from ...services.extraction_service import ExtractionService

router = APIRouter(prefix="/analytics", tags=["analytics"])

# Initialize services
search_algorithms = SearchAlgorithms()
aggregation_algorithms = AggregationAlgorithms()
extraction_service = ExtractionService()

@router.post("/sort", response_model=SortResponse)
async def sort_receipts(
    sort_options: SortOptions,
    db: Session = Depends(get_db)
):
    """
    Sort receipts using various algorithms.
    
    Args:
        sort_options: Sorting parameters
        db: Database session
        
    Returns:
        SortResponse with sorted results
    """
    start_time = time.time()
    
    try:
        # Get all receipts from database
        db_receipts = db.query(Receipt).all()
        
        # Convert to list of dictionaries for algorithm processing
        receipts = []
        for receipt in db_receipts:
            # Parse items properly - ensure it's always a list
            try:
                items = extraction_service.parse_items_json(receipt.items_json)
                if not isinstance(items, list):
                    items = []
            except Exception:
                items = []
            
            receipt_dict = {
                'id': receipt.id,
                'vendor': receipt.vendor,
                'transaction_date': receipt.transaction_date.strftime('%Y-%m-%d'),
                'amount': receipt.amount,
                'currency': receipt.currency,
                'category': receipt.category,
                'confidence_score': receipt.confidence_score,
                'file_name': receipt.filename,
                'items': items,
                'extracted_text': receipt.raw_text,
                'upload_timestamp': receipt.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            receipts.append(receipt_dict)
        
        # Perform sorting
        reverse = sort_options.order == 'desc'
        results = search_algorithms.sort(
            receipts,
            field=sort_options.field,
            algorithm=sort_options.algorithm,
            reverse=reverse
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
                file_size=0,
                confidence_score=result['confidence_score'],
                extracted_text=result['extracted_text'],
                upload_timestamp=result['upload_timestamp']
            )
            receipt_data_list.append(receipt_data)
        
        execution_time = (time.time() - start_time) * 1000
        
        return SortResponse(
            results=receipt_data_list,
            algorithm_used=sort_options.algorithm,
            execution_time_ms=execution_time,
            sort_info={
                'field': sort_options.field,
                'order': sort_options.order
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Sorting failed: {str(e)}"
        )

@router.post("/aggregate", response_model=AggregationResponse)
async def aggregate_receipts(
    agg_request: AggregationRequest,
    db: Session = Depends(get_db)
):
    """
    Perform statistical aggregations on receipt data.
    
    Args:
        agg_request: Aggregation parameters
        db: Database session
        
    Returns:
        AggregationResponse with results
    """
    start_time = time.time()
    
    try:
        # Get all receipts from database
        db_receipts = db.query(Receipt).all()
        
        # Convert to list of dictionaries
        receipts = []
        for receipt in db_receipts:
            # Parse items properly - ensure it's always a list
            try:
                items = extraction_service.parse_items_json(receipt.items_json)
                if not isinstance(items, list):
                    items = []
            except Exception:
                items = []
            
            receipt_dict = {
                'id': receipt.id,
                'vendor': receipt.vendor,
                'transaction_date': receipt.transaction_date.strftime('%Y-%m-%d'),
                'amount': receipt.amount,
                'currency': receipt.currency,
                'category': receipt.category,
                'confidence_score': receipt.confidence_score,
                'file_name': receipt.filename,
                'items': items,
                'extracted_text': receipt.raw_text,
                'upload_timestamp': receipt.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            receipts.append(receipt_dict)
        
        # Perform aggregation
        if agg_request.function == 'histogram':
            result = aggregation_algorithms.aggregate(
                receipts,
                function=agg_request.function,
                field=agg_request.field,
                bins=agg_request.bins or 10
            )
        elif agg_request.function == 'time_series':
            result = aggregation_algorithms.aggregate(
                receipts,
                function=agg_request.function,
                field=agg_request.field,
                time_field=agg_request.time_field,
                window=agg_request.window
            )
        else:
            result = aggregation_algorithms.aggregate(
                receipts,
                function=agg_request.function,
                field=agg_request.field
            )
        
        execution_time = (time.time() - start_time) * 1000
        
        return AggregationResponse(
            result=result,
            function_used=agg_request.function,
            execution_time_ms=execution_time,
            aggregation_info={
                'field': agg_request.field,
                'time_field': agg_request.time_field,
                'window': agg_request.window,
                'bins': agg_request.bins
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Aggregation failed: {str(e)}"
        )

@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics(db: Session = Depends(get_db)):
    """
    Get comprehensive system statistics.
    
    Args:
        db: Database session
        
    Returns:
        StatisticsResponse with system statistics
    """
    try:
        # Basic statistics
        total_receipts = db.query(Receipt).count()
        total_spend = db.query(func.sum(Receipt.amount)).scalar() or 0.0
        
        # Top vendors
        top_vendors = db.query(
            Receipt.vendor,
            func.count(Receipt.id).label('count'),
            func.sum(Receipt.amount).label('total_amount')
        ).group_by(Receipt.vendor).order_by(func.count(Receipt.id).desc()).limit(10).all()
        
        top_vendors_list = [
            {
                'vendor': vendor,
                'count': count,
                'total_amount': float(total_amount)
            }
            for vendor, count, total_amount in top_vendors
        ]
        
        # Category breakdown
        category_breakdown = db.query(
            Receipt.category,
            func.count(Receipt.id).label('count'),
            func.sum(Receipt.amount).label('total_amount')
        ).group_by(Receipt.category).all()
        
        category_list = [
            {
                'category': category,
                'count': count,
                'total_amount': float(total_amount)
            }
            for category, count, total_amount in category_breakdown
        ]
        
        # Monthly trends
        monthly_trends = db.query(
            func.strftime('%Y-%m', Receipt.transaction_date).label('month'),
            func.count(Receipt.id).label('count'),
            func.sum(Receipt.amount).label('total_amount')
        ).group_by(func.strftime('%Y-%m', Receipt.transaction_date)).order_by('month').all()
        
        monthly_list = [
            {
                'month': month,
                'count': count,
                'total_amount': float(total_amount)
            }
            for month, count, total_amount in monthly_trends
        ]
        
        # Advanced statistics
        avg_amount = db.query(func.avg(Receipt.amount)).scalar() or 0.0
        max_amount = db.query(func.max(Receipt.amount)).scalar() or 0.0
        avg_confidence = db.query(func.avg(Receipt.confidence_score)).scalar() or 0.0
        
        advanced_stats = {
            'avg_receipt_amount': float(avg_amount),
            'most_expensive_receipt': float(max_amount),
            'confidence_avg': float(avg_confidence)
        }
        
        return StatisticsResponse(
            total_receipts=total_receipts,
            total_spend=float(total_spend),
            top_vendors=top_vendors_list,
            category_breakdown=category_list,
            monthly_trends=monthly_list,
            advanced_stats=advanced_stats
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Statistics failed: {str(e)}"
        )

@router.get("/algorithms", response_model=AlgorithmInfoResponse)
async def get_algorithm_info():
    """
    Get information about available algorithms.
    
    Returns:
        AlgorithmInfoResponse with algorithm details
    """
    return AlgorithmInfoResponse(
        search_algorithms=search_algorithms.get_algorithm_info(),
        sort_algorithms={
            'quicksort': 'O(n log n) average - Quick sort',
            'mergesort': 'O(n log n) - Merge sort',
            'timsort': 'O(n log n) - Tim sort',
            'heapsort': 'O(n log n) - Heap sort'
        },
        aggregation_functions={
            'sum': 'Sum of values',
            'mean': 'Average of values',
            'median': 'Median of values',
            'mode': 'Most common value',
            'variance': 'Variance of values',
            'std_dev': 'Standard deviation',
            'histogram': 'Distribution histogram',
            'time_series': 'Time-based aggregations'
        }
    ) 