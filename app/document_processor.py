from google.cloud import documentai
from google.api_core.client_options import ClientOptions
import pandas as pd
from typing import Dict, List, Optional
from config.settings import settings


class DocumentProcessor:
    def __init__(self):
        self.client = documentai.DocumentProcessorServiceClient(
            client_options=ClientOptions(
                api_endpoint=f"{settings.PROCESSOR_LOCATION}-documentai.googleapis.com"
            )
        )
        self.processor_name = self.client.processor_path(
            settings.PROJECT_ID,
            settings.PROCESSOR_LOCATION,
            settings.PROCESSOR_ID
        )

    def process_document(self, file_content: bytes, mime_type: str) -> Dict:
        """Process document using Document AI"""
        request = documentai.ProcessRequest(
            name=self.processor_name,
            raw_document=documentai.RawDocument(
                content=file_content,
                mime_type=mime_type
            )
        )

        result = self.client.process_document(request=request)
        return self._extract_invoice_data(result.document)

    def _extract_invoice_data(self, document) -> Dict:
        """Extract structured data from invoice"""
        invoice_data = {
            'vendor_info': {},
            'invoice_details': {},
            'line_items': [],
            'totals': {},
            'raw_text': document.text
        }

        # Extract entities
        for entity in document.entities:
            if entity.type_ == "supplier_name":
                invoice_data['vendor_info']['name'] = entity.mention_text
            elif entity.type_ == "supplier_address":
                invoice_data['vendor_info']['address'] = entity.mention_text
            elif entity.type_ == "invoice_id":
                invoice_data['invoice_details']['invoice_id'] = entity.mention_text
            elif entity.type_ == "invoice_date":
                invoice_data['invoice_details']['date'] = entity.mention_text
            elif entity.type_ == "total_amount":
                invoice_data['totals']['total'] = entity.mention_text
            elif entity.type_ == "line_item":
                invoice_data['line_items'].append(self._parse_line_item(entity))

        return invoice_data

    def _parse_line_item(self, entity) -> Dict:
        """Parse individual line item"""
        line_item = {
            'description': '',
            'quantity': '',
            'unit_price': '',
            'total_price': ''
        }

        for prop in entity.properties:
            if prop.type_ == "line_item/description":
                line_item['description'] = prop.mention_text
            elif prop.type_ == "line_item/quantity":
                line_item['quantity'] = prop.mention_text
            elif prop.type_ == "line_item/unit_price":
                line_item['unit_price'] = prop.mention_text
            elif prop.type_ == "line_item/amount":
                line_item['total_price'] = prop.mention_text

        return line_item