import os
import json
import streamlit as st
import tempfile
from PIL import Image
from src.helper import setup_api_keys, process_pdf, find_table_images, process_table_image, extract_financial_data

# Page configuration
st.set_page_config(
    page_title="Financial PDF Data Extractor",
    page_icon="📊",
)

# Initialize session state for selected sample
if 'selected_sample' not in st.session_state:
    st.session_state.selected_sample = None

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

# Sample PDF section
st.subheader("Use Sample PDF")
st.markdown("Click on one of the sample PDFs below to test the application:")

# Get list of sample PDFs
sample_pdfs = [f for f in os.listdir("data") if f.endswith(".pdf")]
sample_pdfs.sort()

# Create columns for sample PDF buttons
sample_cols = st.columns(min(4, len(sample_pdfs)))

# Function to handle sample selection
def select_sample(pdf_file):
    st.session_state.selected_sample = os.path.join("data", pdf_file)

# Create buttons for each sample PDF
for i, pdf_file in enumerate(sample_pdfs):
    col_idx = i % len(sample_cols)
    with sample_cols[col_idx]:
        if st.button(f"Sample {i+1}: {pdf_file}", key=f"sample_btn_{i}", 
                    type="secondary" if st.session_state.selected_sample != os.path.join("data", pdf_file) else "primary"):
            select_sample(pdf_file)

# Clear sample selection button
if st.session_state.selected_sample:
    if st.button("Clear Sample Selection", type="secondary"):
        st.session_state.selected_sample = None

# File uploader
st.subheader("Or Upload Your Own PDF")
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

# Process the selected file (either uploaded or sample)
pdf_to_process = None
pdf_name = None

if st.session_state.selected_sample:
    pdf_to_process = st.session_state.selected_sample
    pdf_name = os.path.basename(st.session_state.selected_sample)
    st.success(f"Using sample PDF: {pdf_name}")
elif uploaded_file is not None:
    # Create a temporary file for the uploaded PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        pdf_to_process = tmp_file.name
    pdf_name = uploaded_file.name

if pdf_to_process:
    # Process button
    if st.button("Process PDF", key="process_btn"):
        try:
            # Create a status container
            status_container = st.container()
            status = status_container.empty()
            status.text("Starting PDF processing...")
            
            # Create progress bar
            progress_bar = st.progress(0)
            
            # Create extraction directory if it doesn't exist
            os.makedirs("extracted_data", exist_ok=True)
            
            # Step 1: Process PDF to extract text elements
            status.text("Step 1/4: Extracting text and tables from PDF...")
            text_data = process_pdf(pdf_to_process)
            progress_bar.progress(25)
            
            # Step 2: Find table images
            status.text("Step 2/4: Identifying table images...")
            table_img_paths = find_table_images("extracted_data")
            progress_bar.progress(50)
            
            # Display the table images
            if table_img_paths:
                status.text(f"Found {len(table_img_paths)} tables in the PDF")
                st.subheader("Extracted Table Images")
                
                # Create columns for displaying images
                cols = st.columns(min(3, len(table_img_paths)))
                
                # Display each table image
                for i, img_path in enumerate(table_img_paths):
                    col_idx = i % len(cols)
                    with cols[col_idx]:
                        img = Image.open(img_path)
                        st.image(img, caption=f"Table {i+1}", use_container_width=True)
                        st.write(f"Processing Table {i+1}...")
            else:
                status.text("No table images found in the PDF")
            
            # Step 3: Process each table image
            status.text(f"Step 3/4: Processing {len(table_img_paths)} table images with Groq LLM...")
            table_data = []
            table_results = []  # Store the extracted table content
            
            for i, img_path in enumerate(table_img_paths):
                sub_status = status_container.empty()
                sub_status.text(f"Processing table {i+1}/{len(table_img_paths)}...")
                table_content = process_table_image(img_path, groq_api_key)
                table_data.append(table_content)
                table_results.append({"table_number": i+1, "content": table_content})
                sub_status.empty()
            progress_bar.progress(75)
            
            # Display the extracted table content
            if table_results:
                st.subheader("Extracted Table Content")
                for i, result in enumerate(table_results):
                    with st.expander(f"Table {result['table_number']} Content"):
                        st.text(result['content'])
            
            # Step 4: Extract structured financial data
            status.text("Step 4/4: Extracting structured financial data with Google Gemini...")
            combined_text = f"Text from PDF {text_data}:\nTable Data:\n{' '.join(table_data)}\n\n"
            financial_data = extract_financial_data(combined_text, google_api_key)
            progress_bar.progress(100)
            
            # Clean up temporary files
            if uploaded_file is not None:  # Only delete if it was an uploaded file
                os.unlink(pdf_to_process)
            if os.path.exists("extracted_data"):
                import shutil
                shutil.rmtree("extracted_data", ignore_errors=True)
            
            # Display the results
            status.text("Processing complete!")
            st.subheader("Extracted Financial Data")
            st.json(financial_data)
            
            # Check if there's a corresponding JSON file for the sample
            if st.session_state.selected_sample:
                json_file_path = st.session_state.selected_sample.replace('.pdf', '.json')
                if os.path.exists(json_file_path):
                    with open(json_file_path, 'r') as f:
                        expected_json = json.load(f)
                    
                    st.subheader("Expected Output (Sample JSON)")
                    st.json(expected_json)
            
            # Download button for JSON
            json_str = json.dumps(financial_data, indent=4)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name=f"{os.path.splitext(pdf_name)[0]}_financial_data.json",
                mime="application/json"
            )
            
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")