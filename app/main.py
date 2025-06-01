import streamlit as st
import pandas as pd
from pathlib import Path
import io
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

from document_processor import DocumentProcessor
from data_processor import DataProcessor
from export_manager import ExportManager
from config.settings import settings

# Page configuration
st.set_page_config(
    page_title="Invoice Processing System",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)


class InvoiceProcessorApp:
    def __init__(self):
        self.doc_processor = DocumentProcessor()
        self.data_processor = DataProcessor()
        self.export_manager = ExportManager()

        # Initialize session state
        if 'processed_data' not in st.session_state:
            st.session_state.processed_data = pd.DataFrame()
        if 'processing_history' not in st.session_state:
            st.session_state.processing_history = []

    def run(self):
        """Main application runner"""
        st.title("🚀 Invoice Processing System")
        st.markdown("### Automate invoice data extraction with AI-powered Document Processing")

        # Sidebar
        self._render_sidebar()

        # Main content
        tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload & Process", "📊 Data View", "📈 Analytics", "⚙️ Settings"])

        with tab1:
            self._render_upload_tab()

        with tab2:
            self._render_data_tab()

        with tab3:
            self._render_analytics_tab()

        with tab4:
            self._render_settings_tab()

    def _render_sidebar(self):
        """Render sidebar with controls"""
        st.sidebar.title("🎛️ Controls")

        # Processing options
        st.sidebar.subheader("Processing Options")
        self.auto_clean = st.sidebar.checkbox("Auto-clean data", value=True)
        self.include_confidence = st.sidebar.checkbox("Include confidence scores", value=False)

        # Export options
        st.sidebar.subheader("Export Options")
        self.export_format = st.sidebar.selectbox(
            "Export Format",
            ["CSV", "Excel", "JSON"],
            index=0
        )

        # Processing history
        st.sidebar.subheader("📋 Processing History")
        if st.session_state.processing_history:
            for i, item in enumerate(st.session_state.processing_history[-5:]):
                st.sidebar.text(f"{i + 1}. {item['filename']} - {item['timestamp']}")
        else:
            st.sidebar.text("No processing history")

        # Clear history button
        if st.sidebar.button("Clear History"):
            st.session_state.processing_history = []
            st.sidebar.success("History cleared!")

    def _render_upload_tab(self):
        """Render file upload and processing tab"""
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("📁 Upload Invoice Files")

            uploaded_files = st.file_uploader(
                "Choose invoice files",
                type=['pdf', 'png', 'jpg', 'jpeg', 'tiff'],
                accept_multiple_files=True,
                help="Upload PDF, PNG, JPG, JPEG, or TIFF files"
            )

            if uploaded_files:
                st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully")

                # Process files button
                if st.button("🚀 Process Files", type="primary"):
                    self._process_files(uploaded_files)

        with col2:
            st.subheader("📋 Processing Status")
            if st.session_state.processed_data.empty:
                st.info("No data processed yet")
            else:
                st.success(f"✅ Processed {len(st.session_state.processed_data)} items")
                st.metric("Total Items", len(st.session_state.processed_data))
                st.metric("Total Value", f"${st.session_state.processed_data['total_price'].sum():.2f}")

    def _process_files(self, uploaded_files):
        """Process uploaded files"""
        progress_bar = st.progress(0)
        status_text = st.empty()

        all_data = []

        for i, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"Processing {uploaded_file.name}...")

            try:
                # Read file content
                file_content = uploaded_file.read()
                mime_type = self._get_mime_type(uploaded_file.name)

                # Process with Document AI
                invoice_data = self.doc_processor.process_document(file_content, mime_type)

                # Convert to DataFrame
                df = self.data_processor.process_invoice_data(invoice_data)

                if not df.empty:
                    df['source_file'] = uploaded_file.name
                    all_data.append(df)

                # Update processing history
                st.session_state.processing_history.append({
                    'filename': uploaded_file.name,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'items_extracted': len(df)
                })

            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {str(e)}")

            progress_bar.progress((i + 1) / len(uploaded_files))

        # Combine all data
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            st.session_state.processed_data = combined_df
            status_text.success(f"✅ Successfully processed {len(uploaded_files)} files!")
        else:
            status_text.warning("⚠️ No data extracted from uploaded files")

    def _render_data_tab(self):
        """Render data viewing and export tab"""
        if st.session_state.processed_data.empty:
            st.info("📝 No data to display. Please upload and process some invoices first.")
            return

        df = st.session_state.processed_data

        # Data filtering
        col1, col2, col3 = st.columns(3)

        with col1:
            vendor_filter = st.multiselect(
                "Filter by Vendor",
                options=df['vendor_name'].unique(),
                default=df['vendor_name'].unique()
            )

        with col2:
            date_range = st.date_input(
                "Date Range",
                value=(df['invoice_date'].min(), df['invoice_date'].max()),
                help="Filter invoices by date range"
            )

        with col3:
            min_amount = st.number_input(
                "Minimum Amount",
                min_value=0.0,
                value=0.0,
                help="Filter items by minimum amount"
            )

        # Apply filters
        filtered_df = df[
            (df['vendor_name'].isin(vendor_filter)) &
            (df['total_price'] >= min_amount)
            ]

        # Display data
        st.subheader(f"📊 Invoice Data ({len(filtered_df)} items)")
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )

        # Export section
        st.subheader("💾 Export Data")
        col1, col2, col3 = st.columns(3)

        with col1:
            export_filename = st.text_input(
                "Export Filename",
                value=f"invoice_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

        with col2:
            if st.button("📥 Export Data", type="primary"):
                try:
                    export_path = self.export_manager.export_data(
                        filtered_df,
                        self.export_format,
                        export_filename
                    )
                    st.success(f"✅ Data exported to: {export_path}")

                    # Provide download link
                    with open(export_path, "rb") as file:
                        st.download_button(
                            label="📥 Download File",
                            data=file.read(),
                            file_name=f"{export_filename}.{self.export_format.lower()}",
                            mime=self._get_download_mime_type(self.export_format)
                        )
                except Exception as e:
                    st.error(f"❌ Export failed: {str(e)}")

    def _render_analytics_tab(self):
        """Render analytics and insights tab"""
        if st.session_state.processed_data.empty:
            st.info("📊 No data for analytics. Please process some invoices first.")
            return

        df = st.session_state.processed_data

        # Summary metrics
        st.subheader("📈 Summary Metrics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Items", len(df))
        with col2:
            st.metric("Total Value", f"${df['total_price'].sum():,.2f}")
        with col3:
            st.metric("Unique Vendors", df['vendor_name'].nunique())
        with col4:
            st.metric("Average Item Value", f"${df['total_price'].mean():.2f}")

        # Charts
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("💰 Spending by Vendor")
            vendor_spending = df.groupby('vendor_name')['total_price'].sum().sort_values(ascending=False)
            fig_vendor = px.bar(
                x=vendor_spending.values,
                y=vendor_spending.index,
                orientation='h',
                title="Total Spending by Vendor"
            )
            st.plotly_chart(fig_vendor, use_container_width=True)

        with col2:
            st.subheader("📅 Spending Over Time")
            if 'invoice_date' in df.columns:
                daily_spending = df.groupby(df['invoice_date'].dt.date)['total_price'].sum()
                fig_time = px.line(
                    x=daily_spending.index,
                    y=daily_spending.values,
                    title="Daily Spending Trend"
                )
                st.plotly_chart(fig_time, use_container_width=True)

        # Item analysis
        st.subheader("🔍 Item Analysis")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🏆 Top Items by Value")
            top_items = df.nlargest(10, 'total_price')[['description', 'total_price', 'vendor_name']]
            st.dataframe(top_items, hide_index=True)

        with col2:
            st.subheader("📊 Price Distribution")
            fig_hist = px.histogram(
                df,
                x='total_price',
                nbins=20,
                title="Item Price Distribution"
            )
            st.plotly_chart(fig_hist, use_container_width=True)

    def _render_settings_tab(self):
        """Render settings and configuration tab"""
        st.subheader("⚙️ Application Settings")

        # Processing settings
        st.subheader("🔧 Processing Configuration")
        col1, col2 = st.columns(2)

        with col1:
            st.text_input("Project ID", value=settings.PROJECT_ID, disabled=True)
            st.text_input("Processor ID", value=settings.PROCESSOR_ID, disabled=True)

        with col2:
            st.text_input("Processor Location", value=settings.PROCESSOR_LOCATION, disabled=True)
            st.number_input("Max File Size (MB)", value=settings.MAX_FILE_SIZE / (1024 * 1024), disabled=True)

        # Data quality settings
        st.subheader("📊 Data Quality")
        confidence_threshold = st.slider(
            "Confidence Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.8,
            help="Minimum confidence score for extracted data"
        )

        # Advanced settings
        st.subheader("🔬 Advanced Settings")
        enable_batch_processing = st.checkbox("Enable Batch Processing", value=True)
        auto_backup = st.checkbox("Auto-backup processed data", value=True)

        # System information
        st.subheader("ℹ️ System Information")
        st.info(f"""
        **Upload Directory**: {settings.UPLOAD_DIR}
        **Export Directory**: {settings.EXPORT_DIR}
        **Supported Formats**: {', '.join(settings.ALLOWED_EXTENSIONS)}
        **Current Session**: {len(st.session_state.processed_data)} items processed
        """)

    def _get_mime_type(self, filename: str) -> str:
        """Get MIME type based on file extension"""
        extension = Path(filename).suffix.lower()
        mime_types = {
            '.pdf': 'application/pdf',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.tiff': 'image/tiff'
        }
        return mime_types.get(extension, 'application/octet-stream')

    def _get_download_mime_type(self, format_type: str) -> str:
        """Get MIME type for download"""
        mime_types = {
            'CSV': 'text/csv',
            'Excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'JSON': 'application/json'
        }
        return mime_types.get(format_type, 'application/octet-stream')


# Run the application
if __name__ == "__main__":
    app = InvoiceProcessorApp()
    app.run()