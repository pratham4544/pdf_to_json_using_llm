import os
import json
import streamlit as st
import tempfile
from src.helper import setup_api_keys, process_pdf_pipeline

# Page configuration
st.set_page_config(
    page_title="Financial PDF Data Extractor",
    page_icon="📊",
)

# App title and description
st.title("Financial PDF Data Extractor")
st.markdown("Upload your PDF file to extract structured financial data.")

# Try to get API keys
try:
    groq_api_key, google_api_key = setup_api_keys()
except Exception as e:
    st.error(f"Error loading API keys: {str(e)}")
    st.info("Make sure you have a .env file in your project root with GROQ_API_KEY and GOOGLE_API_KEY defined.")
    st.stop()

# File uploader
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file is not None:
    # Process button
    if st.button("Process PDF"):
        try:
            # Show processing message
            status = st.empty()
            status.text("Processing PDF...")
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                pdf_path = tmp_file.name
            
            # Run the extraction pipeline
            financial_data = process_pdf_pipeline(pdf_path, groq_api_key, google_api_key)
            
            # Clean up temporary file
            os.unlink(pdf_path)
            
            # Display the results
            status.text("Processing complete!")
            st.subheader("Extracted Financial Data")
            st.json(financial_data)
            
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