import pandas as pd
import json
from pathlib import Path
from typing import Dict, Any
import xlsxwriter
from config.settings import settings


class ExportManager:
    def __init__(self):
        self.export_formats = ['CSV', 'Excel', 'JSON']

    def export_data(self, df: pd.DataFrame, format_type: str, filename: str) -> str:
        """Export data in specified format"""
        export_path = settings.EXPORT_DIR / f"{filename}.{format_type.lower()}"

        if format_type.upper() == 'CSV':
            return self._export_csv(df, export_path)
        elif format_type.upper() == 'EXCEL':
            return self._export_excel(df, export_path)
        elif format_type.upper() == 'JSON':
            return self._export_json(df, export_path)
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    def _export_csv(self, df: pd.DataFrame, path: Path) -> str:
        """Export to CSV format"""
        df.to_csv(path, index=False, encoding='utf-8')
        return str(path)

    def _export_excel(self, df: pd.DataFrame, path: Path) -> str:
        """Export to Excel format with formatting"""
        with pd.ExcelWriter(path, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Invoice_Data', index=False)

            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Invoice_Data']

            # Add formatting
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })

            # Write headers with formatting
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)

            # Auto-adjust column widths
            for i, col in enumerate(df.columns):
                max_length = max(df[col].astype(str).map(len).max(), len(col))
                worksheet.set_column(i, i, min(max_length + 2, 50))

        return str(path)

    def _export_json(self, df: pd.DataFrame, path: Path) -> str:
        """Export to JSON format"""
        # Convert DataFrame to JSON with proper date handling
        json_data = df.to_dict('records')

        # Custom JSON encoder for datetime
        def json_serializer(obj):
            if pd.isna(obj):
                return None
            if hasattr(obj, 'isoformat'):
                return obj.isoformat()
            return str(obj)

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, default=json_serializer, ensure_ascii=False)

        return str(path)

    def create_summary_report(self, summary_stats: Dict, export_path: Path) -> str:
        """Create a summary report"""
        report_path = export_path / "summary_report.json"

        with open(report_path, 'w') as f:
            json.dump(summary_stats, f, indent=2, default=str)

        return str(report_path)