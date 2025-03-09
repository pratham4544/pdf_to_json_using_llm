import streamlit as st
from src.helper import *
from src.prompt import template

# Streamlit UI
st.title("PDF to JSON Converter")

uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if st.button("Process PDF") and uploaded_file is not None:
    pdf_name = uploaded_file.name
    text = load_pdf_data(pdf_name)
    st.write(f'pdf file read successfully')
    prompt = prompt_generator(template)
    st.write('prompt generated')
    response = llm_chain(model, parser, prompt, text)
    st.json(response)