import streamlit as st
import sys
from pathlib import Path

# Add app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

if __name__ == "__main__":
    from app.main import InvoiceProcessorApp

    app = InvoiceProcessorApp()
    app.run()