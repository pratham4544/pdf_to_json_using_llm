import base64
import os
import re
import json
from typing import Dict, Any, List
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from unstructured.partition.pdf import partition_pdf

# Simple prompt for extracting financial data
extract_financial_data_prompt = """
Extract structured financial data from the given content and format it as JSON.
Include key financial metrics, tables, and statements found in the document.

Content to analyze:
{context}

{format_instructions}
"""

def setup_api_keys():
    """Set up API keys from .env file"""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API keys from environment variables
    groq_api_key = os.getenv("GROQ_API_KEY")
    google_api_key = os.getenv("GOOGLE_API_KEY")
    
    if not groq_api_key or not google_api_key:
        raise ValueError("API keys are missing. Please set GROQ_API_KEY and GOOGLE_API_KEY in your .env file.")
    
    return groq_api_key, google_api_key

def process_pdf(pdf_path: str) -> str:
    """Extract elements from PDF file"""
    elements = partition_pdf(
        filename=pdf_path,
        strategy="hi_res",
        extract_images_in_pdf=True,
        extract_image_block_types=["Image", "Table"],
        extract_image_block_to_payload=False,
        extract_image_block_output_dir="extracted_data"
    )
    
    # Extract tables as text
    tables = []
    for element in elements:
        if "unstructured.documents.elements.Table" in str(type(element)):
            tables.append(str(element))
    
    text_data = ' '.join(tables)
    return text_data

def find_table_images(extraction_dir: str) -> List[str]:
    """Find all table images in the extraction directory"""
    table_img_paths = []
    
    if os.path.exists(extraction_dir):
        for filename in os.listdir(extraction_dir):
            if re.match(r"table-\d+-\d+\.jpg", filename):
                table_img_paths.append(os.path.join(extraction_dir, filename))
    
    return table_img_paths

def encode_image(image_path: str) -> str:
    """Encode image to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def process_table_image(image_path: str, groq_api_key: str) -> str:
    """Process a table image and extract its content"""
    # Encode image to base64
    base64_image = encode_image(image_path)
    
    # Set up chat model
    chat = ChatGroq(model_name="llama-3.2-11b-vision-preview", api_key=groq_api_key)
    
    # Define prompt
    prompt = """
    You are an expert at extracting tabular data from images.
    Analyze the provided image, which contains a table. Identify all the columns and rows.
    Represent the table in a structured format. Do not include any other text except the tabular data.
    
    Return the table in CSV format. If there are merged cells,
    represent the data in the merged cells in each row where they appear.
    """
    
    # Process the image
    msg = chat.invoke(
        [
            HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ]
            )
        ]
    )
    
    return msg.content

def extract_financial_data(content: str, google_api_key: str) -> Dict[str, Any]:
    """Extract structured financial data from text content"""
    # Set up model and parser
    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash", 
        api_key=google_api_key,
        temperature=0.5
    )
    parser = JsonOutputParser()
    
    # Create the prompt
    prompt_template = PromptTemplate(
        template=extract_financial_data_prompt,
        input_variables=["context"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    # Create and run the chain
    chain = prompt_template | model | parser
    
    try:
        # Extract structured data
        response = chain.invoke({"context": content})
        return response
    except Exception as e:
        print(f"Error parsing data: {str(e)}")
        
        # Try to fix the JSON with another model call
        output = model.invoke(f"Fix this JSON and ensure it's properly formatted:\n{content}")
        cleaned_output = output.content.replace("```json", "").replace("```", "").strip()
        
        try:
            return json.loads(cleaned_output)
        except:
            return {"error": "Could not parse the financial data", "raw_content": cleaned_output}

def process_pdf_pipeline(pdf_path: str, groq_api_key: str, google_api_key: str) -> Dict[str, Any]:
    """Complete pipeline to process PDF and extract financial data"""
    # Create extraction directory if it doesn't exist
    os.makedirs("extracted_data", exist_ok=True)
    
    # Process PDF to extract text elements
    text_data = process_pdf(pdf_path)
    
    # Find and process table images
    table_img_paths = find_table_images("extracted_data")
    
    # Process each table image
    table_data = []
    for img_path in table_img_paths:
        table_content = process_table_image(img_path, groq_api_key)
        table_data.append(table_content)
    
    # Combine all data
    combined_text = f"Text from PDF {text_data}:\nTable Data:\n{' '.join(table_data)}\n\n"
    
    # Extract structured financial data
    financial_data = extract_financial_data(combined_text, google_api_key)
    
    # Clean up temporary directories
    if os.path.exists("extracted_data"):
        import shutil
        shutil.rmtree("extracted_data", ignore_errors=True)
    
    return financial_data