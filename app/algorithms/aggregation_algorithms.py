"""
Aggregation algorithms for the OCR Receipt Processor.
Implements statistical functions and data analysis operations.
"""

import statistics
import math
from typing import List, Dict, Any, Optional
from collections import defaultdict, Counter
from datetime import datetime, timedelta

class AggregationAlgorithms:
    """Collection of aggregation algorithms for receipt data."""
    
    def __init__(self):
        """Initialize aggregation algorithms."""
        self.functions = {
            'sum': self._sum,
            'mean': self._mean,
            'median': self._median,
            'mode': self._mode,
            'variance': self._variance,
            'std_dev': self._std_deviation,
            'histogram': self._histogram,
            'time_series': self._time_series_aggregation
        }
    
    def _sum(self, receipts: List[Dict], field: str = 'amount') -> float:
        """
        Calculate sum of values.
        
        Args:
            receipts: List of receipt dictionaries
            field: Field to sum
            
        Returns:
            Sum of values
        """
        values = []
        for receipt in receipts:
            value = receipt.get(field)
            if value is not None:
                try:
                    values.append(float(value))
                except (ValueError, TypeError):
                    continue
        
        return sum(values) if values else 0.0
    
    def _mean(self, receipts: List[Dict], field: str = 'amount') -> float:
        """
        Calculate mean (average) of values.
        
        Args:
            receipts: List of receipt dictionaries
            field: Field to calculate mean for
            
        Returns:
            Mean of values
        """
        values = []
        for receipt in receipts:
            value = receipt.get(field)
            if value is not None:
                try:
                    values.append(float(value))
                except (ValueError, TypeError):
                    continue
        
        return statistics.mean(values) if values else 0.0
    
    def _median(self, receipts: List[Dict], field: str = 'amount') -> float:
        """
        Calculate median of values.
        
        Args:
            receipts: List of receipt dictionaries
            field: Field to calculate median for
            
        Returns:
            Median of values
        """
        values = []
        for receipt in receipts:
            value = receipt.get(field)
            if value is not None:
                try:
                    values.append(float(value))
                except (ValueError, TypeError):
                    continue
        
        return statistics.median(values) if values else 0.0
    
    def _mode(self, receipts: List[Dict], field: str = 'vendor') -> List[Any]:
        """
        Calculate mode (most common values).
        
        Args:
            receipts: List of receipt dictionaries
            field: Field to calculate mode for
            
        Returns:
            List of most common values
        """
        values = []
        for receipt in receipts:
            value = receipt.get(field)
            if value is not None:
                values.append(str(value))
        
        if not values:
            return []
        
        counter = Counter(values)
        max_count = max(counter.values())
        return [value for value, count in counter.items() if count == max_count]
    
    def _variance(self, receipts: List[Dict], field: str = 'amount') -> float:
        """
        Calculate variance of values.
        
        Args:
            receipts: List of receipt dictionaries
            field: Field to calculate variance for
            
        Returns:
            Variance of values
        """
        values = []
        for receipt in receipts:
            value = receipt.get(field)
            if value is not None:
                try:
                    values.append(float(value))
                except (ValueError, TypeError):
                    continue
        
        return statistics.variance(values) if len(values) > 1 else 0.0
    
    def _std_deviation(self, receipts: List[Dict], field: str = 'amount') -> float:
        """
        Calculate standard deviation of values.
        
        Args:
            receipts: List of receipt dictionaries
            field: Field to calculate standard deviation for
            
        Returns:
            Standard deviation of values
        """
        values = []
        for receipt in receipts:
            value = receipt.get(field)
            if value is not None:
                try:
                    values.append(float(value))
                except (ValueError, TypeError):
                    continue
        
        return statistics.stdev(values) if len(values) > 1 else 0.0
    
    def _histogram(self, receipts: List[Dict], field: str = 'amount', bins: int = 10) -> Dict[str, Any]:
        """
        Generate histogram data.
        
        Args:
            receipts: List of receipt dictionaries
            field: Field to create histogram for
            bins: Number of bins
            
        Returns:
            Histogram data with bins and counts
        """
        values = []
        for receipt in receipts:
            value = receipt.get(field)
            if value is not None:
                values.append(str(value))
        
        if not values:
            return {'bins': [], 'counts': [], 'min_value': 0, 'max_value': 0}
        
        # Check if values are numeric
        numeric_values = []
        for value in values:
            try:
                numeric_values.append(float(value))
            except (ValueError, TypeError):
                continue
        
        # If we have numeric values, create numeric histogram
        if numeric_values:
            min_val = min(numeric_values)
            max_val = max(numeric_values)
            
            if min_val == max_val:
                return {'bins': [min_val], 'counts': [len(numeric_values)], 'min_value': min_val, 'max_value': max_val}
            
            bin_size = (max_val - min_val) / bins
            bin_counts = [0] * bins
            
            for value in numeric_values:
                bin_index = min(int((value - min_val) / bin_size), bins - 1)
                bin_counts[bin_index] += 1
            
            bin_edges = [min_val + i * bin_size for i in range(bins + 1)]
            
            return {
                'bins': bin_edges,
                'counts': bin_counts,
                'min_value': min_val,
                'max_value': max_val,
                'bin_size': bin_size
            }
        else:
            # For categorical data, create frequency distribution
            counter = Counter(values)
            sorted_items = sorted(counter.items(), key=lambda x: x[1], reverse=True)
            
            # Take top bins items
            top_items = sorted_items[:bins]
            
            return {
                'bins': [item[0] for item in top_items],
                'counts': [item[1] for item in top_items],
                'min_value': 0,
                'max_value': len(counter),
                'frequency_distribution': dict(sorted_items)
            }
    
    def _time_series_aggregation(self, receipts: List[Dict], field: str = 'amount', 
                                time_field: str = 'transaction_date', window: str = 'monthly') -> List[Dict[str, Any]]:
        """
        Perform time series aggregation.
        
        Args:
            receipts: List of receipt dictionaries
            field: Field to aggregate
            time_field: Time field for grouping
            window: Time window (daily, weekly, monthly)
            
        Returns:
            List of time series data points
        """
        # Group by time window
        grouped_data = defaultdict(list)
        
        for receipt in receipts:
            time_value = receipt.get(time_field)
            if time_value is None:
                continue
            
            try:
                if isinstance(time_value, str):
                    date_obj = datetime.strptime(time_value, '%Y-%m-%d')
                else:
                    date_obj = time_value
                
                # Create time key based on window
                if window == 'daily':
                    time_key = date_obj.strftime('%Y-%m-%d')
                elif window == 'weekly':
                    # Get the start of the week (Monday)
                    days_since_monday = date_obj.weekday()
                    week_start = date_obj - timedelta(days=days_since_monday)
                    time_key = week_start.strftime('%Y-%m-%d')
                elif window == 'monthly':
                    time_key = date_obj.strftime('%Y-%m')
                else:
                    time_key = date_obj.strftime('%Y-%m-%d')
                
                value = receipt.get(field)
                if value is not None:
                    try:
                        # For time series, we want to count receipts per time period
                        # rather than sum numeric values
                        if field == time_field:
                            grouped_data[time_key].append(1)  # Count receipts
                        else:
                            grouped_data[time_key].append(float(value))
                    except (ValueError, TypeError):
                        if field == time_field:
                            grouped_data[time_key].append(1)  # Count receipts
                        continue
                        
            except (ValueError, TypeError):
                continue
        
        # Calculate aggregations for each time period
        result = []
        for time_key in sorted(grouped_data.keys()):
            values = grouped_data[time_key]
            if values:
                result.append({
                    'time_period': time_key,
                    'count': len(values),
                    'sum': sum(values),
                    'mean': statistics.mean(values),
                    'min': min(values),
                    'max': max(values)
                })
        
        return result
    
    def aggregate(self, receipts: List[Dict], function: str, field: str = 'amount', **kwargs) -> Any:
        """
        Perform aggregation using specified function.
        
        Args:
            receipts: List of receipt dictionaries
            function: Aggregation function to use
            field: Field to aggregate
            **kwargs: Additional function-specific parameters
            
        Returns:
            Aggregation result
        """
        if function not in self.functions:
            raise ValueError(f"Unknown aggregation function: {function}")
        
        return self.functions[function](receipts, field, **kwargs)
    
    def get_function_info(self) -> Dict[str, str]:
        """Get information about available aggregation functions."""
        return {
            'sum': 'Sum of values',
            'mean': 'Average of values',
            'median': 'Median of values',
            'mode': 'Most common value',
            'variance': 'Variance of values',
            'std_dev': 'Standard deviation',
            'histogram': 'Distribution histogram',
            'time_series': 'Time-based aggregations'
        } 