"""
Sorting algorithms for the OCR Receipt Processor.
Implements various sorting strategies with different time complexities.
"""

from typing import List, Dict, Any, Callable

class SortAlgorithms:
    """Collection of sorting algorithms for receipt data."""
    
    def __init__(self):
        """Initialize sorting algorithms."""
        self.algorithms = {
            'quicksort': self._quicksort,
            'mergesort': self._mergesort,
            'timsort': self._timsort,
            'heapsort': self._heapsort
        }
    
    def _quicksort(self, receipts: List[Dict], field: str, reverse: bool = False) -> List[Dict]:
        """
        QuickSort implementation - O(n log n) average case.
        
        Args:
            receipts: List of receipt dictionaries
            field: Field to sort by
            reverse: Sort in descending order if True
            
        Returns:
            Sorted list of receipts
        """
        def get_field_value(receipt):
            if hasattr(receipt, field):
                return getattr(receipt, field)
            else:
                return receipt.get(field, '')
        
        def partition(arr, low, high):
            pivot = get_field_value(arr[high])
            i = low - 1
            
            for j in range(low, high):
                if (get_field_value(arr[j]) <= pivot) != reverse:
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]
            
            arr[i + 1], arr[high] = arr[high], arr[i + 1]
            return i + 1
        
        def quicksort_recursive(arr, low, high):
            if low < high:
                pi = partition(arr, low, high)
                quicksort_recursive(arr, low, pi - 1)
                quicksort_recursive(arr, pi + 1, high)
        
        receipts_copy = receipts.copy()
        quicksort_recursive(receipts_copy, 0, len(receipts_copy) - 1)
        return receipts_copy
    
    def _mergesort(self, receipts: List[Dict], field: str, reverse: bool = False) -> List[Dict]:
        """
        MergeSort implementation - O(n log n) time complexity.
        
        Args:
            receipts: List of receipt dictionaries
            field: Field to sort by
            reverse: Sort in descending order if True
            
        Returns:
            Sorted list of receipts
        """
        def get_field_value(receipt):
            if hasattr(receipt, field):
                return getattr(receipt, field)
            else:
                return receipt.get(field, '')
        
        def merge(left, right):
            result = []
            i = j = 0
            
            while i < len(left) and j < len(right):
                left_val = get_field_value(left[i])
                right_val = get_field_value(right[j])
                
                if (left_val <= right_val) != reverse:
                    result.append(left[i])
                    i += 1
                else:
                    result.append(right[j])
                    j += 1
            
            result.extend(left[i:])
            result.extend(right[j:])
            return result
        
        def mergesort_recursive(arr):
            if len(arr) <= 1:
                return arr
            
            mid = len(arr) // 2
            left = mergesort_recursive(arr[:mid])
            right = mergesort_recursive(arr[mid:])
            
            return merge(left, right)
        
        return mergesort_recursive(receipts)
    
    def _timsort(self, receipts: List[Dict], field: str, reverse: bool = False) -> List[Dict]:
        """
        TimSort implementation - O(n log n) time complexity.
        Uses Python's built-in sorted function which implements TimSort.
        
        Args:
            receipts: List of receipt dictionaries
            field: Field to sort by
            reverse: Sort in descending order if True
            
        Returns:
            Sorted list of receipts
        """
        def get_field_value(receipt):
            if hasattr(receipt, field):
                return getattr(receipt, field)
            else:
                return receipt.get(field, '')
        
        return sorted(receipts, key=get_field_value, reverse=reverse)
    
    def _heapsort(self, receipts: List[Dict], field: str, reverse: bool = False) -> List[Dict]:
        """
        HeapSort implementation - O(n log n) time complexity.
        
        Args:
            receipts: List of receipt dictionaries
            field: Field to sort by
            reverse: Sort in descending order if True
            
        Returns:
            Sorted list of receipts
        """
        def get_field_value(receipt):
            if hasattr(receipt, field):
                return getattr(receipt, field)
            else:
                return receipt.get(field, '')
        
        def heapify(arr, n, i):
            largest = i
            left = 2 * i + 1
            right = 2 * i + 2
            
            if left < n:
                left_val = get_field_value(arr[left])
                largest_val = get_field_value(arr[largest])
                if (left_val > largest_val) != reverse:
                    largest = left
            
            if right < n:
                right_val = get_field_value(arr[right])
                largest_val = get_field_value(arr[largest])
                if (right_val > largest_val) != reverse:
                    largest = right
            
            if largest != i:
                arr[i], arr[largest] = arr[largest], arr[i]
                heapify(arr, n, largest)
        
        receipts_copy = receipts.copy()
        n = len(receipts_copy)
        
        # Build max heap
        for i in range(n // 2 - 1, -1, -1):
            heapify(receipts_copy, n, i)
        
        # Extract elements from heap one by one
        for i in range(n - 1, 0, -1):
            receipts_copy[0], receipts_copy[i] = receipts_copy[i], receipts_copy[0]
            heapify(receipts_copy, i, 0)
        
        return receipts_copy
    
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
        if algorithm not in self.algorithms:
            raise ValueError(f"Unknown sorting algorithm: {algorithm}")
        
        return self.algorithms[algorithm](receipts, field, reverse)
    
    def get_algorithm_info(self) -> Dict[str, str]:
        """Get information about available sorting algorithms."""
        return {
            'quicksort': 'O(n log n) average - Quick sort',
            'mergesort': 'O(n log n) - Merge sort',
            'timsort': 'O(n log n) - Tim sort (Python default)',
            'heapsort': 'O(n log n) - Heap sort'
        } 