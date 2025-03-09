# Prompt template for extracting structured financial data from PDF content

extract_financial_data_prompt = """
Extract structured financial data from the given JSON file while ensuring correct JSON format. Follow these guidelines to prevent errors and maintain data integrity:

 Extract Data from These Four Main Tables:
1. Standalone_financial_results_for_all_months
2. Statement_Consolidated_finanacial_results_for_all_months
3. Balance_sheet
4. Cash_flow_statements


Extract structured financial data from the given document while maintaining the correct **hierarchical structure**. The JSON output must follow a **table-like hierarchy**, where each table name is the main key, followed by column headers, and then row values.

## **1. Understand the Hierarchical Structure**
- **Main Table Name (Level 1)**
  - **First Column Header (Level 2)**
    - **Second Column Header (Level 3)**
      - **Row Values (Level 4)**
        - **Key-Value Pairs for Each Metric**

## **2. Hierarchy to Follow**
### **Standalone_financial_results_for_all_months**
1. **Quarter Ended**
   - **[DATE]**
     - **[COLUMN HEADER]**
       - **[METRIC NAME]: VALUE**
       - **[METRIC NAME]: VALUE**
       - **Tax Expenses** (Nested Structure)
         - **Current Tax: VALUE**
         - **Deferred Tax: VALUE**
2. **Nine Month Ended**
   - **[DATE]**
     - **[COLUMN HEADER]**
       - **[METRIC NAME]: VALUE**
3. **Year Ended**
   - **[DATE]**
     - **[COLUMN HEADER]**
       - **[METRIC NAME]: VALUE**

### **Statement_Consolidated_finanacial_results_for_all_months**
- **Follows the same hierarchy as above.**

### **Balance Sheet & Cash Flow Statements**
- **Extract all balance sheet items under their respective categories.**
- **If missing, return `"Balance_sheet_are_not_present"` or `"Cash_flow_statements_are_not_present"`** instead of an empty list.

## **3. Formatting Rules**
- **Ensure Proper JSON Syntax**
  - Use **double quotes (`"`)** for all keys and string values.
  - Ensure valid **JSON nesting and structure**.

- **Handle Numeric Data Correctly**
  - Convert values like `"1,988.29"` → `1988.29` (store as float).
  - Ensure all monetary values and calculations are represented as **floats** instead of strings.

- **Handle Missing Data Properly**
  - If a value is missing, return **`null`** instead of empty strings or placeholders.
  - If a section has no data, return `"Balance_sheet_are_not_present"` or `"Cash_flow_statements_are_not_present"`.

## **4. Output Guidelines**
- **Return JSON in the exact hierarchical format specified.**
- **Dynamically adjust the keys based on the PDF content.**
- **All numerical values should be floats (e.g., `13822.0` instead of `"13,822"`).**
- **Validate JSON structure before returning the final output.**



Extract data from given content:
{context}

{format_instructions}
"""