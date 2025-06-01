import pytest
import pandas as pd
from unittest.mock import Mock, patch
from app.document_processor import DocumentProcessor
from app.data_processor import DataProcessor


class TestDocumentProcessor:
    def setup_method(self):
        self.processor = DocumentProcessor()

    @patch('app.document_processor.documentai')
    def test_process_document(self, mock_documentai):
        """Test document processing"""
        # Mock response
        mock_response = Mock()
        mock_response.document.text = "Test invoice text"
        mock_response.document.entities = []

        mock_documentai.DocumentProcessorServiceClient.return_value.process_document.return_value = mock_response

        result = self.processor.process_document(b"test content", "application/pdf")

        assert isinstance(result, dict)
        assert 'vendor_info' in result
        assert 'invoice_details' in result
        assert 'line_items' in result


class TestDataProcessor:
    def setup_method(self):
        self.processor = DataProcessor()

    def test_process_invoice_data(self):
        """Test invoice data processing"""
        test_data = {
            'line_items': [
                {
                    'description': 'Test Item',
                    'quantity': '2',
                    'unit_price': '10.00',
                    'total_price': '20.00'
                }
            ],
            'vendor_info': {'name': 'Test Vendor'},
            'invoice_details': {'invoice_id': 'INV-001'}
        }

        result = self.processor.process_invoice_data(test_data)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert 'description' in result.columns