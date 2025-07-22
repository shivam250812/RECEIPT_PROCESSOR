"""
Search algorithms for the OCR Receipt Processor.
Implements various search strategies with different time complexities.
"""

import re
import hashlib
from typing import List, Dict, Any, Optional
from collections import defaultdict

class SearchAlgorithms:
    """Collection of search algorithms for receipt data."""
    
    def __init__(self):
        """Initialize search algorithms."""
        self.algorithms = {
            'linear': self._linear_search,
            'binary': self._binary_search,
            'hash': self._hash_search,
            'fuzzy': self._fuzzy_search,
            'range': self._range_search,
            'pattern': self._pattern_search
        }
    
    def _linear_search(self, receipts: List[Dict], query: str, field: str = 'vendor') -> List[Dict]:
        """
        Linear search implementation - O(n) time complexity.
        Simple sequential search through all receipts.
        
        Args:
            receipts: List of receipt dictionaries
            query: Search query string
            field: Field to search in
            
        Returns:
            List of matching receipts
        """
        results = []
        query_lower = query.lower()
        
        for receipt in receipts:
            if hasattr(receipt, field):
                field_value = str(getattr(receipt, field, '')).lower()
            else:
                field_value = str(receipt.get(field, '')).lower()
            if query_lower in field_value:
                results.append(receipt)
        
        return results
    
    def _binary_search(self, receipts: List[Dict], query: str, field: str = 'vendor') -> List[Dict]:
        """
        Binary search implementation - O(log n) time complexity.
        Requires sorted data by the search field.
        
        Args:
            receipts: List of receipt dictionaries
            query: Search query string
            field: Field to search in
            
        Returns:
            List of matching receipts
        """
        def get_field_value(receipt):
            if hasattr(receipt, field):
                return str(getattr(receipt, field, ''))
            else:
                return str(receipt.get(field, ''))
        
        # First sort by the field
        sorted_receipts = sorted(receipts, key=get_field_value)
        
        results = []
        query_lower = query.lower()
        
        def binary_search_recursive(arr, left, right):
            if left > right:
                return
            
            mid = (left + right) // 2
            mid_value = get_field_value(arr[mid]).lower()
            
            if query_lower in mid_value:
                # Found a match, check surrounding elements for more matches
                results.append(arr[mid])
                
                # Check left side
                i = mid - 1
                while i >= 0 and query_lower in get_field_value(arr[i]).lower():
                    results.append(arr[i])
                    i -= 1
                
                # Check right side
                i = mid + 1
                while i < len(arr) and query_lower in get_field_value(arr[i]).lower():
                    results.append(arr[i])
                    i += 1
                    
            elif query_lower < mid_value:
                binary_search_recursive(arr, left, mid - 1)
            else:
                binary_search_recursive(arr, mid + 1, right)
        
        binary_search_recursive(sorted_receipts, 0, len(sorted_receipts) - 1)
        return results
    
    def _hash_search(self, receipts: List[Dict], query: str, field: str = 'vendor') -> List[Dict]:
        """
        Hash-based search implementation - O(1) average case.
        Uses hash indexing for fast lookups.
        
        Args:
            receipts: List of receipt dictionaries
            query: Search query string
            field: Field to search in
            
        Returns:
            List of matching receipts
        """
        # Build hash index
        hash_index = defaultdict(list)
        
        for receipt in receipts:
            field_value = str(receipt.get(field, '')).lower()
            # Create hash of the field value
            hash_key = hashlib.md5(field_value.encode()).hexdigest()
            hash_index[hash_key].append(receipt)
            
            # Also index by words for partial matching
            words = field_value.split()
            for word in words:
                word_hash = hashlib.md5(word.encode()).hexdigest()
                hash_index[word_hash].append(receipt)
        
        # Search using hash
        query_lower = query.lower()
        query_hash = hashlib.md5(query_lower.encode()).hexdigest()
        
        results = []
        if query_hash in hash_index:
            results.extend(hash_index[query_hash])
        
        # Remove duplicates
        seen = set()
        unique_results = []
        for receipt in results:
            receipt_id = receipt.get('id')
            if receipt_id not in seen:
                seen.add(receipt_id)
                unique_results.append(receipt)
        
        return unique_results
    
    def _fuzzy_search(self, receipts: List[Dict], query: str, field: str = 'vendor', threshold: float = 0.7) -> List[Dict]:
        """
        Fuzzy search implementation using Levenshtein distance.
        Returns results with similarity above threshold.
        
        Args:
            receipts: List of receipt dictionaries
            query: Search query string
            field: Field to search in
            threshold: Similarity threshold (0.0 to 1.0)
            
        Returns:
            List of matching receipts with similarity scores
        """
        def levenshtein_distance(s1: str, s2: str) -> int:
            """Calculate Levenshtein distance between two strings."""
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
            
            if len(s2) == 0:
                return len(s1)
            
            previous_row = list(range(len(s2) + 1))
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            
            return previous_row[-1]
        
        def similarity(s1: str, s2: str) -> float:
            """Calculate similarity ratio between two strings."""
            distance = levenshtein_distance(s1.lower(), s2.lower())
            max_len = max(len(s1), len(s2))
            if max_len == 0:
                return 1.0
            return 1 - (distance / max_len)
        
        results = []
        query_lower = query.lower()
        
        for receipt in receipts:
            field_value = str(receipt.get(field, '')).lower()
            sim = similarity(query_lower, field_value)
            
            if sim >= threshold:
                receipt['similarity_score'] = sim
                results.append(receipt)
        
        # Sort by similarity score
        results.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
        return results
    
    def _range_search(self, receipts: List[Dict], min_value: Any = None, max_value: Any = None, field: str = 'amount') -> List[Dict]:
        """
        Range search implementation for numeric fields.
        
        Args:
            receipts: List of receipt dictionaries
            min_value: Minimum value for range
            max_value: Maximum value for range
            field: Field to search in
            
        Returns:
            List of receipts within the specified range
        """
        results = []
        
        for receipt in receipts:
            field_value = receipt.get(field)
            if field_value is None:
                continue
            
            # Convert to float for numeric comparison
            try:
                numeric_value = float(field_value)
            except (ValueError, TypeError):
                continue
            
            # Check range conditions
            if min_value is not None and numeric_value < min_value:
                continue
            if max_value is not None and numeric_value > max_value:
                continue
            
            results.append(receipt)
        
        return results
    
    def _pattern_search(self, receipts: List[Dict], pattern: str, field: str = 'vendor') -> List[Dict]:
        """
        Pattern search implementation using regex.
        
        Args:
            receipts: List of receipt dictionaries
            pattern: Regex pattern to search for
            field: Field to search in
            
        Returns:
            List of receipts matching the pattern
        """
        results = []
        
        try:
            regex = re.compile(pattern, re.IGNORECASE)
        except re.error:
            return results
        
        for receipt in receipts:
            field_value = str(receipt.get(field, ''))
            if regex.search(field_value):
                results.append(receipt)
        
        return results
    
    def search(self, receipts: List[Dict], query: str, algorithm: str = 'linear', 
               field: str = 'vendor', **kwargs) -> List[Dict]:
        """
        Perform search using specified algorithm.
        
        Args:
            receipts: List of receipt dictionaries
            query: Search query
            algorithm: Search algorithm to use
            field: Field to search in
            **kwargs: Additional algorithm-specific parameters
            
        Returns:
            List of matching receipts
        """
        if algorithm not in self.algorithms:
            raise ValueError(f"Unknown search algorithm: {algorithm}")
        
        return self.algorithms[algorithm](receipts, query, field, **kwargs)
    
    def get_algorithm_info(self) -> Dict[str, str]:
        """Get information about available search algorithms."""
        return {
            'linear': 'O(n) - Simple sequential search',
            'binary': 'O(log n) - Binary search on sorted data',
            'hash': 'O(1) average - Hash-based fast lookup',
            'fuzzy': 'O(n*m) - Approximate string matching',
            'range': 'O(n) - Numeric range queries',
            'pattern': 'O(n) - Regex pattern matching'
        }
    
    def sort(self, receipts: List[Dict], field: str, algorithm: str = 'timsort', 
             reverse: bool = False) -> List[Dict]:
        """
        Sort receipts using specified algorithm.
        
        Args:
            receipts: List of receipt dictionaries
            field: Field to sort by
            algorithm: Sorting algorithm to use
            reverse: Sort in descending order if True
            
        Returns:
            Sorted list of receipts
        """
        from .sort_algorithms import SortAlgorithms
        sort_algo = SortAlgorithms()
        return sort_algo.sort(receipts, field, algorithm, reverse)
    
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
        from .aggregation_algorithms import AggregationAlgorithms
        agg_algo = AggregationAlgorithms()
        return agg_algo.aggregate(receipts, function, field, **kwargs) 