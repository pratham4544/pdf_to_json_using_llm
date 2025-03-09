from pypdf import PdfReader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
load_dotenv()
        
        
model = ChatGroq(model_name="llama-3.2-3b-preview")
parser = JsonOutputParser()

def load_pdf_data(file_path):
    loader = PyPDFLoader(file_path, mode="page")
    text = loader.load()
    return text 

def prompt_generator(base_template):
    prompt = PromptTemplate(
    template="""
"Extract financial data from the provided PDF files into a structured JSON format. The JSON should have the following structure:

- `Standalone_financial_results_for_all_months`: a dictionary with quarter/year ended as keys and financial data as values
- `Statement_Consolidated_finanacial_results_for_all_months`: a dictionary with quarter/year ended as keys and consolidated financial data as values
- `Balance_sheet` and `Cash_flow_statements`: include these keys in the output, but for this example, include a string placeholder value since the actual data is not provided.

Example of expected JSON structure:
```json
{{
    "Standalone_financial_results_for_all_months": {{
        "Quarter ended 31 December 2024": {{
            "Revenue from operations": 15437.85,
            "Other income": 599.98,
            ...
        }},
        ...
    }},
    "Statement_Consolidated_finanacial_results_for_all_months": {{
        "Quarter ended 31 December 2024": {{
            "Revenue from operations": 16175.71,
            "Other income": 1301.15,
            ...
        }},
        ...
    }},
    "Balance_sheet": "Balance_sheet_are_not_present",
    "Cash_flow_statements": "Cash_flow_statements_are_not_present"
}}
```
Please ensure the extracted data is accurate and complete, and follows the provided structure."

### **Extracted Table Data:**
{context}


\n{format_instructions}\n"""
Please ensure the extracted data is accurate and complete, and follows the provided structure."

### **Extracted Table Data:**
{context}


\n{format_instructions}\n""",
    input_variables=["context"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

    return prompt

def llm_chain(model, parser,prompt, text):
    chain = prompt | model | parser
    response = chain.invoke({"context": text})
    return response