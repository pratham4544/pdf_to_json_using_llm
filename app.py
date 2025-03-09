import os
import json
import streamlit as st
import tempfile
import subprocess
import sys
from src.helper import setup_api_keys, process_pdf_pipeline

# Check for poppler installation
def check_poppler_installed():
    try:
        # Try to call pdftoppm (part of poppler-utils)
        result = subprocess.run(['pdftoppm', '-v'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except FileNotFoundError:
        return False

# Page configuration
st.set_page_config(
    page_title="Financial PDF Data Extractor",
    page_icon="📊",
    layout="wide"
)

# App title and description
st.title("Financial PDF Data Extractor")
st.markdown("""
This application extracts structured financial data from PDF files containing tables and financial statements.
Upload your PDF file, click the 'Process PDF' button, and get the data in structured JSON format.
""")

# Check for necessary system dependencies
poppler_installed = check_poppler_installed()
if not poppler_installed:
    st.error("""
    ### 🚨 Required dependency not found: poppler-utils
    
    This application requires poppler-utils to process PDF files.
    
    #### Installation instructions:
    
    **For Ubuntu/Debian:**
    ```bash
    sudo apt-get update
    sudo apt-get install poppler-utils
    ```
    
    **For macOS (using Homebrew):**
    ```bash
    brew install poppler
    ```
    
    **For Windows:**
    1. Download from: https://github.com/oschwartz10612/poppler-windows/releases/
    2. Extract the files
    3. Add the `bin` directory to your PATH environment variable
    
    Please install the required dependency and restart the application.
    """)
    
    # Provide a way to continue anyway for testing purposes
    proceed_anyway = st.checkbox("I've installed poppler-utils but it's not being detected correctly. Proceed anyway (may fail)")
    if not proceed_anyway:
        st.stop()

# Sidebar for API keys (if not using secrets)
with st.sidebar:
    st.header("API Keys Configuration")
    st.info("If you haven't set up API keys in environment variables or secrets, you can enter them here:")
    
    user_groq_api_key = st.text_input("GROQ API Key (for vision model)", type="password")
    user_google_api_key = st.text_input("Google API Key (for text models)", type="password")
    
    st.markdown("---")
    st.markdown("""
    ### How it works
    1. Upload a PDF containing financial data
    2. The app extracts text and tables from the PDF
    3. Images of tables are processed using GROQ's vision model
    4. All data is combined and structured into JSON
    5. Results can be downloaded as a JSON file
    """)
    
    st.markdown("---")
    st.markdown("""
    ### System Requirements
    This application requires several system dependencies:
    
    - **poppler-utils**: For PDF processing
    - **tesseract-ocr**: For OCR capabilities (optional)
    
    Installation commands for Ubuntu/Debian:
    ```bash
    sudo apt-get update
    sudo apt-get install poppler-utils
    sudo apt-get install libleptonica-dev tesseract-ocr libtesseract-dev
    ```
    """)

# Try to get API keys from environment or secrets, if not provided by user
try:
    groq_api_key, google_api_key = setup_api_keys()
    # Override with user input if provided
    if user_groq_api_key:
        groq_api_key = user_groq_api_key
    if user_google_api_key:
        google_api_key = user_google_api_key
except Exception as e:
    if not (user_groq_api_key and user_google_api_key):
        st.error("API keys are required. Please provide them in the sidebar.")
        st.stop()
    else:
        groq_api_key = user_groq_api_key
        google_api_key = user_google_api_key

# File uploader
uploaded_file = st.file_uploader("Upload a PDF file containing financial data", type=["pdf"])

if uploaded_file is not None:
    # Display file details
    file_details = {"Filename": uploaded_file.name, "File size": f"{uploaded_file.size / 1024:.2f} KB"}
    st.write(file_details)
    
    # Create a progress bar and status message
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Process button
    if st.button("Process PDF"):
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                pdf_path = tmp_file.name
            
            # Process the PDF
            status_text.text("Extracting data from PDF...")
            progress_bar.progress(25)
            
            status_text.text("Processing tables and images...")
            progress_bar.progress(50)
            
            # Run the extraction pipeline
            financial_data = process_pdf_pipeline(pdf_path, groq_api_key, google_api_key)
            
            status_text.text("Structuring financial data...")
            progress_bar.progress(75)
            
            # Clean up temporary file
            os.unlink(pdf_path)
            
            # Complete
            progress_bar.progress(100)
            status_text.text("Processing complete!")
            
            # Display the results
            st.subheader("Extracted Financial Data")
            
            # Create tabs for different views
            tab1, tab2 = st.tabs(["Formatted JSON", "Raw JSON"])
            
            with tab1:
                st.json(financial_data)
            
            with tab2:
                st.code(json.dumps(financial_data, indent=4), language="json")
            
            # Download button for JSON
            json_str = json.dumps(financial_data, indent=4)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name=f"{os.path.splitext(uploaded_file.name)[0]}_financial_data.json",
                mime="application/json"
            )
            
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")
            st.markdown("""
            ### Troubleshooting
            
            If you're seeing 'Unable to get page count. Is poppler installed and in PATH?', please:
            
            1. Make sure you've installed poppler-utils as mentioned in the sidebar
            2. Check that poppler is in your system PATH
            3. Restart the application after installation
            
            For more details, see the error message below:
            """)
            import traceback
            st.code(traceback.format_exc())
        finally:
            # Make sure to clean up temporary directories if they exist
            if os.path.exists("extracted_data"):
                import shutil
                shutil.rmtree("extracted_data", ignore_errors=True)

# Footer
st.markdown("---")
st.caption("© 2025 Financial PDF Data Extractor - Powered by Groq and Google Generative AI")