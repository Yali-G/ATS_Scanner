# parsers.py
import PyPDF2 # pip install PyPDF2
from docx import Document # pip install python-docx
import io # Used for handling file objects from Streamlit
import sys
import fitz  # PyMuPDF, pip install PyMuPDF

def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        # PyMuPDF can directly open file-like objects
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        for page in doc:
            # extract_text() usually preserves lines and spacing much better
            text += page.get_text("text") # "text" for plain text, "json" or "dict" for structured output
            text += "\n" # Add a newline between pages
        doc.close()
    except Exception as e:
        print(f"Error reading PDF with PyMuPDF: {e}")
        return None
    return text

def extract_text_from_docx(docx_file):
    text = ""
    try:
        # python-docx can directly open the file object
        document = Document(docx_file)
        for paragraph in document.paragraphs:
            text += paragraph.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX: {e}")
        return None
    return text

# ...existing code...

def main():
    if len(sys.argv) != 2:
        print("Usage: python parsers.py <path_to_pdf>")
        return
    pdf_path = sys.argv[1]
    try:
        with open(pdf_path, "rb") as f:
            text = extract_text_from_pdf(f)
            if text:
                print("Extracted text:\n")
                print(text)
            else:
                print("No text extracted.")
    except Exception as e:
        print(f"Failed to open or parse PDF: {e}")

if __name__ == "__main__":
    main()
# ...existing code...

# Note: You might want to add a function for plain text if you support direct paste of resume
# def get_text_input(input_string):
#     return input_string