# Financial PDF Data Extractor

This application extracts structured financial data from PDF files and converts them into a standardized JSON format. It uses advanced AI models to process tables and financial statements from your documents.

## Features

- Extract financial data from PDF documents
- Process tables in PDF using AI-based image recognition
- Structure data into well-organized JSON
- User-friendly web interface built with Streamlit
- Download processed data as JSON files

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/financial-pdf-extractor.git
cd financial-pdf-extractor
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Install system dependencies

#### Ubuntu/Debian:

```bash
sudo apt-get update
sudo apt-get install poppler-utils
sudo apt-get install libleptonica-dev tesseract-ocr libtesseract-dev python3-pil tesseract-ocr-eng tesseract-ocr-script-latn
```

#### macOS:

```bash
brew install poppler
brew install tesseract
```

#### Windows:

1. **Poppler:**
   - Download from: https://github.com/oschwartz10612/poppler-windows/releases/
   - Extract the files
   - Add the `bin` directory to your PATH environment variable

2. **Tesseract:**
   - Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
   - Run the installer
   - Add the installation directory to your PATH environment variable

### 4. Set up API keys

Create a `.streamlit/secrets.toml` file with your API keys:

```toml
GROQ_API_KEY = "your-groq-api-key"
GOOGLE_API_KEY = "your-google-api-key"
```

You can also set these as environment variables:

```bash
export GROQ_API_KEY="your-groq-api-key"
export GOOGLE_API_KEY="your-google-api-key"
```

## Running the application

```bash
streamlit run app.py
```

Then open your browser and go to http://localhost:8501

## Troubleshooting

### Poppler not found

If you get the error "Unable to get page count. Is poppler installed and in PATH?":

1. Verify poppler is installed:
   ```bash
   pdftoppm -v
   ```
   
2. Make sure it's in your PATH:
   - For Windows, check your Environment Variables
   - For Linux/macOS, add to PATH if needed:
     ```bash
     export PATH=$PATH:/path/to/poppler/bin
     ```

3. Restart your terminal or application

### Other issues

- Check that all system dependencies are correctly installed
- Verify that your API keys are valid and have the necessary permissions
- Ensure your PDF file is not corrupted or password-protected

## Project Structure

```
financial-pdf-extractor/
├── app.py                # Main Streamlit application
├── src/
│   ├── prompt.py         # Prompts for AI models
│   └── helper.py         # Helper functions
├── requirements.txt      # Python dependencies
└── .streamlit/
    └── secrets.toml      # API keys (not in repository)
```

## License

[MIT License](LICENSE)