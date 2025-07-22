"""
Pydantic models for the OCR Receipt Processor API.
Defines request/response schemas with validation.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

class ReceiptData(BaseModel):
    """Receipt data model for API responses."""
    id: int
    vendor: str
    transaction_date: str
    amount: float
    currency: str = "USD"
    category: str
    items: List[Dict[str, Any]] = []
    file_name: str
    file_size: int
    confidence_score: float
    extracted_text: str
    upload_timestamp: str
    
    model_config = {
        'from_attributes': True
    }

class SearchQuery(BaseModel):
    """Search query model with algorithm selection."""
    query: str = Field(..., description="Search query string")
    algorithm: str = Field(
        default="linear",
        pattern='^(linear|binary|hash|fuzzy|range|pattern)$',
        description="Search algorithm to use"
    )
    field: str = Field(
        default="vendor",
        pattern='^(vendor|transaction_date|amount|category|confidence_score)$',
        description="Field to search in"
    )
    threshold: Optional[float] = Field(
        None, 
        ge=0.0, 
        le=1.0,
        description="Similarity threshold for fuzzy search"
    )
    min_value: Optional[Union[float, str]] = Field(
        None,
        description="Minimum value for range search"
    )
    max_value: Optional[Union[float, str]] = Field(
        None,
        description="Maximum value for range search"
    )
    pattern: Optional[str] = Field(
        None,
        description="Regex pattern for pattern search"
    )

class SortOptions(BaseModel):
    """Sorting options model."""
    field: str = Field(
        ...,
        pattern='^(vendor|transaction_date|amount|category|confidence_score)$',
        description="Field to sort by"
    )
    order: str = Field(
        default="asc",
        pattern='^(asc|desc)$',
        description="Sort order (ascending or descending)"
    )
    algorithm: str = Field(
        default="timsort",
        pattern='^(quicksort|mergesort|timsort|heapsort)$',
        description="Sorting algorithm to use"
    )

class AggregationRequest(BaseModel):
    """Aggregation request model."""
    function: str = Field(
        ...,
        pattern='^(sum|mean|median|mode|variance|std_dev|histogram|time_series)$',
        description="Aggregation function to apply"
    )
    field: str = Field(
        default="amount",
        pattern='^(vendor|transaction_date|amount|category|confidence_score)$',
        description="Field to aggregate"
    )
    time_field: Optional[str] = Field(
        None,
        pattern='^(transaction_date|upload_timestamp)$',
        description="Time field for time series aggregation"
    )
    window: Optional[str] = Field(
        None,
        pattern='^(daily|weekly|monthly)$',
        description="Time window for aggregation"
    )
    bins: Optional[int] = Field(
        None,
        ge=1,
        le=100,
        description="Number of bins for histogram"
    )

class SearchResponse(BaseModel):
    """Search response model."""
    results: List[ReceiptData]
    total_count: int
    algorithm_used: str
    execution_time_ms: float
    query_info: Dict[str, Any]

class SortResponse(BaseModel):
    """Sort response model."""
    results: List[ReceiptData]
    algorithm_used: str
    execution_time_ms: float
    sort_info: Dict[str, Any]

class AggregationResponse(BaseModel):
    """Aggregation response model."""
    result: Any
    function_used: str
    execution_time_ms: float
    aggregation_info: Dict[str, Any]

class AlgorithmInfoResponse(BaseModel):
    """Algorithm information response model."""
    search_algorithms: Dict[str, str]
    sort_algorithms: Dict[str, str]
    aggregation_functions: Dict[str, str]

class FileUploadResponse(BaseModel):
    """File upload response model."""
    message: str
    receipt_id: int
    extracted_data: ReceiptData

class StatisticsResponse(BaseModel):
    """Statistics response model."""
    total_receipts: int
    total_spend: float
    top_vendors: List[Dict[str, Any]]
    category_breakdown: List[Dict[str, Any]]
    monthly_trends: List[Dict[str, Any]]
    advanced_stats: Optional[Dict[str, Any]] = None

class HealthCheckResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: datetime
    version: str
    database_connected: bool
    services_healthy: Dict[str, bool] 