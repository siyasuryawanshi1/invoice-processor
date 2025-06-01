import pandas as pd
import numpy as np
from typing import Dict, List
import re
from datetime import datetime


class DataProcessor:
    def __init__(self):
        self.processed_data = None

    def process_invoice_data(self, invoice_data: Dict) -> pd.DataFrame:
        """Convert invoice data to structured DataFrame"""
        line_items = invoice_data.get('line_items', [])

        if not line_items:
            return pd.DataFrame()

        # Create DataFrame from line items
        df = pd.DataFrame(line_items)

        # Add invoice metadata
        df['invoice_id'] = invoice_data.get('invoice_details', {}).get('invoice_id', '')
        df['vendor_name'] = invoice_data.get('vendor_info', {}).get('name', '')
        df['invoice_date'] = invoice_data.get('invoice_details', {}).get('date', '')
        df['processed_timestamp'] = datetime.now().isoformat()

        # Clean and standardize data
        df = self._clean_data(df)

        self.processed_data = df
        return df

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize the data"""
        # Clean numeric fields
        numeric_columns = ['quantity', 'unit_price', 'total_price']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].apply(self._extract_numeric)

        # Clean text fields
        text_columns = ['description', 'vendor_name']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].str.strip().str.title()

        # Parse dates
        if 'invoice_date' in df.columns:
            df['invoice_date'] = pd.to_datetime(df['invoice_date'], errors='coerce')

        return df

    def _extract_numeric(self, value: str) -> float:
        """Extract numeric value from string"""
        if pd.isna(value) or value == '':
            return 0.0

        # Remove currency symbols and extract numbers
        numeric_str = re.sub(r'[^\d.,]', '', str(value))
        numeric_str = numeric_str.replace(',', '')

        try:
            return float(numeric_str)
        except ValueError:
            return 0.0

    def get_summary_statistics(self) -> Dict:
        """Generate summary statistics"""
        if self.processed_data is None or self.processed_data.empty:
            return {}

        df = self.processed_data

        return {
            'total_items': len(df),
            'total_amount': df['total_price'].sum(),
            'average_item_price': df['total_price'].mean(),
            'unique_vendors': df['vendor_name'].nunique(),
            'date_range': {
                'start': df['invoice_date'].min(),
                'end': df['invoice_date'].max()
            }
        }