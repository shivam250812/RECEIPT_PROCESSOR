"""
Data extraction service for the OCR Receipt Processor.
Handles parsing and extraction of receipt data from OCR text.
"""

import re
import json
import ast
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from dateutil import parser as date_parser

class ExtractionService:
    """Service for extracting structured data from OCR text."""
    
    def parse_items_json(self, raw_items):
        """Parse items_json field from database with robust error handling"""
        if not raw_items:
            return []
        
        if isinstance(raw_items, list):
            return raw_items
        
        if isinstance(raw_items, str):
            # Try JSON parsing first
            try:
                return json.loads(raw_items)
            except Exception:
                # Try Python literal evaluation
                try:
                    return ast.literal_eval(raw_items)
                except Exception:
                    # If both fail, use empty list
                    return []
        
        return []
    
    def extract_vendor(self, text: str) -> str:
        """Extract vendor name from receipt text"""
        lines = text.split('\n')
        
        # Look for vendor in first few lines
        for i, line in enumerate(lines[:5]):
            line = line.strip()
            if line and len(line) > 3 and not line.isdigit():
                # Remove common receipt words
                vendor = re.sub(r'\b(store|shop|market|receipt|invoice|bill)\b', '', line, flags=re.IGNORECASE)
                vendor = vendor.strip()
                if vendor:
                    return vendor[:50]  # Limit length
        
        return "Unknown Vendor"
    
    def extract_amount(self, text: str) -> float:
        """Extract total amount from receipt text"""
        # Look for total amount patterns
        patterns = [
            r'total[:\s]*\$?(\d+\.?\d*)',
            r'amount[:\s]*\$?(\d+\.?\d*)',
            r'balance[:\s]*\$?(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*$',  # Amount at end of line
            r'\$(\d+\.?\d*)',    # Dollar amount
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    # Get the largest amount (likely the total)
                    amounts = [float(match) for match in matches]
                    return max(amounts)
                except ValueError:
                    continue
        
        return 0.0
    
    def extract_date(self, text: str) -> str:
        """Extract date from receipt text"""
        # Common date patterns
        patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',  # MM/DD/YYYY or DD/MM/YYYY
            r'(\d{4})-(\d{1,2})-(\d{1,2})',           # YYYY-MM-DD
            r'(\d{1,2})\s+(\w+)\s+(\d{4})',           # DD Month YYYY
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    # Try to parse the first match
                    match = matches[0]
                    if len(match) == 3:
                        if len(match[2]) == 4:  # Full year
                            return f"{match[0]}/{match[1]}/{match[2]}"
                        else:  # 2-digit year
                            return f"{match[0]}/{match[1]}/20{match[2]}"
                except:
                    continue
        
        # Return today's date if no date found
        return datetime.now().strftime('%Y-%m-%d')
    
    def extract_items(self, text: str) -> List[Dict[str, Any]]:
        """Extract individual items from receipt text"""
        items = []
        lines = text.split('\n')
        
        # Look for item patterns
        item_patterns = [
            r'(\d+)\s+(.+?)\s+\$?(\d+\.?\d*)',  # Quantity Item Price
            r'(.+?)\s+\$?(\d+\.?\d*)',           # Item Price
        ]
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 5:
                continue
            
            for pattern in item_patterns:
                matches = re.findall(pattern, line, re.IGNORECASE)
                if matches:
                    for match in matches:
                        if len(match) == 3:
                            # Quantity Item Price format
                            quantity = int(match[0])
                            item_name = match[1].strip()
                            price = float(match[2])
                        else:
                            # Item Price format
                            quantity = 1
                            item_name = match[0].strip()
                            price = float(match[1])
                        
                        if item_name and price > 0:
                            items.append({
                                'name': item_name,
                                'quantity': quantity,
                                'price': price,
                                'total': quantity * price
                            })
        
        return items
    
    def classify_category(self, text: str) -> str:
        """Classify receipt category based on keywords"""
        text_lower = text.lower()
        
        # Electricity bills
        if any(keyword in text_lower for keyword in ['electricity', 'power', 'energy', 'utility', 'electric']):
            return "Electricity"
        
        # Internet bills
        if any(keyword in text_lower for keyword in ['internet', 'wifi', 'broadband', 'cable', 'telecom']):
            return "Internet"
        
        # Groceries
        if any(keyword in text_lower for keyword in ['grocery', 'supermarket', 'food', 'market', 'store']):
            return "Groceries"
        
        # Gas/Transportation
        if any(keyword in text_lower for keyword in ['gas', 'fuel', 'petrol', 'gasoline', 'transport']):
            return "Transportation"
        
        # Restaurants
        if any(keyword in text_lower for keyword in ['restaurant', 'cafe', 'dining', 'food', 'meal']):
            return "Dining"
        
        # Shopping
        if any(keyword in text_lower for keyword in ['shop', 'store', 'retail', 'clothing', 'electronics']):
            return "Shopping"
        
        return "Other"
    
    def calculate_confidence_score(self, text: str, amount: float) -> float:
        """Calculate confidence score based on text quality and amount extraction"""
        if not text or len(text.strip()) < 10:
            return 0.0
        
        # Base confidence on text length and quality
        text_length = len(text)
        word_count = len(text.split())
        
        # Higher confidence for longer, more detailed text
        length_score = min(text_length / 100, 1.0)
        word_score = min(word_count / 20, 1.0)
        
        # Bonus for amount extraction
        amount_score = 1.0 if amount > 0 else 0.0
        
        # Bonus for having vendor, date, and items
        vendor_score = 1.0 if self.extract_vendor(text) != "Unknown Vendor" else 0.0
        date_score = 1.0 if self.extract_date(text) != datetime.now().strftime('%Y-%m-%d') else 0.0
        items_score = 1.0 if self.extract_items(text) else 0.0
        
        # Calculate weighted average
        confidence = (
            length_score * 0.2 +
            word_score * 0.2 +
            amount_score * 0.2 +
            vendor_score * 0.2 +
            date_score * 0.1 +
            items_score * 0.1
        )
        
        return min(confidence, 1.0)
    
    def parse_receipt_text(self, text: str, file_name: str, file_size: int) -> Dict[str, Any]:
        """Parse receipt text and extract structured data"""
        # Extract basic information
        vendor = self.extract_vendor(text)
        amount = self.extract_amount(text)
        date_str = self.extract_date(text)
        category = self.classify_category(text)
        items = self.extract_items(text)
        confidence_score = self.calculate_confidence_score(text, amount)
        
        # Parse date
        try:
            transaction_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except:
            transaction_date = datetime.now().date()
        
        return {
            'vendor': vendor,
            'amount': amount,
            'transaction_date': transaction_date.strftime('%Y-%m-%d'),
            'category': category,
            'currency': 'USD',
            'items': items,
            'confidence_score': confidence_score,
            'file_name': file_name,
            'file_size': file_size,
            'extracted_text': text
        } 