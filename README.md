# Invoice Processing App

An AI-powered Streamlit application that automates invoice data extraction using Google Cloud Document AI.  
It enables users to upload invoices in various formats (PDF, PNG, JPG, JPEG, TIFF), extract structured data, and export it to CSV, Excel, or JSON formats.

---

## Features

- **Automated Invoice Parsing**: Utilizes Google Cloud Document AI's Invoice Parser to extract key information from invoices.
- **Multi-format Support**: Handles various file formats including PDF, PNG, JPG, JPEG, and TIFF.
- **Data Export**: Exports processed data to CSV, Excel, or JSON formats.

---

## Project Structure

```bash
invoice-processor/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Streamlit main app
│   ├── document_processor.py   # Document AI integration
│   ├── data_processor.py       # Data processing logic
│   ├── export_manager.py       # Export functionality
│   └── utils.py                # Utility functions
├── config/
│   ├── __init__.py
│   ├── settings.py             # Configuration settings
│   └── credentials.json        # Service account key
├── data/
│   ├── uploads/                # Uploaded files
│   ├── processed/              # Processed data
│   └── exports/                # Exported files
├── tests/
│   ├── __init__.py
│   ├── test_document_processor.py
│   └── test_data_processor.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
└── run.py                      # Application entry point
```
---

## Setup Instructions

Follow these steps to set up and run the Invoice Processing App:

### Clone the Repository

```bash
git clone https://github.com/siyasuryawanshi1/invoice-processor.git
cd invoice-processor
```
### Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
### Install Dependencies
```bash
pip install -r requirements.txt
```
### Configure Environment Variables
Create a .env file in the root directory with the following content:
```bash
GOOGLE_APPLICATION_CREDENTIALS=config/credentials.json
PROJECT_ID=your-google-cloud-project-id
PROCESSOR_ID=your-document-ai-processor-id
PROCESSOR_LOCATION=your-processor-location
```
 Replace the placeholder values with actual credentials and project-specific details.
### Google Cloud Document AI Setup
- Enable the API: Visit Google Cloud Console and enable the Document AI API.
- Create a Processor: Set up an Invoice Parser processor in Document AI.
- Generate Service Account:
- Go to IAM & Admin > Service Accounts.
- Create a new account with the Document AI API User role.
- Download the JSON key and save it as credentials.json

### Running the Application
```bash
streamlit run run.py
```