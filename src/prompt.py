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