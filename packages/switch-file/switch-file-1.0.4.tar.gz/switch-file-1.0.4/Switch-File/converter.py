# importing dependencies
import sys
import os
import argparse
import img2pdf
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from reportlab.lib.styles import getSampleStyleSheet
import win32com.client

# Function to convert images to PDF
def convert_images_to_pdf(input_path, output_pdf):
    if os.path.isdir(input_path):
        # If input is a directory, convert all images in the folder to a PDF
        img_files = [f for f in os.listdir(input_path) if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp"))]
        if not img_files:
            print("No images found in the input folder.")
            return

        with open(output_pdf, "wb") as pdf_file:
            # Create a list of image file paths
            images = [os.path.join(input_path, img) for img in img_files]
            # Convert the list of images to a PDF
            pdf_file.write(img2pdf.convert(images))

        print(f"Images converted to PDF: {output_pdf}")
    elif input_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
        # If input is a single image, convert it to a PDF
        with open(output_pdf, "wb") as pdf_file:
            pdf_file.write(img2pdf.convert(input_path))

        print(f"Image converted to PDF: {output_pdf}")
    else:
        print("Unsupported file format. Supported formats: JPG, JPEG, PNG, GIF, BMP")

# Function to convert a text file to PDF

def convert_text_to_pdf(input_file, output_pdf):
    doc = SimpleDocTemplate(output_pdf, pagesize=letter)
    content = []
    styles = getSampleStyleSheet()
    style = styles["Normal"]

    with open(input_file, 'r', encoding='utf-8') as txt_file:
        for line in txt_file:
            # Create paragraphs from each line of text
            content.append(Paragraph(line.strip(), style))

    # Build the PDF document
    doc.build(content)
    print(f"Text file converted to PDF: {output_pdf}")

# Function to convert an XLSX file to PDF

def convert_xlsx_to_pdf(input_xlsx, output_pdf):
    try:
        if not os.path.exists(input_xlsx):
            print(f"Error: Input XLSX file '{input_xlsx}' not found.")
            return

        # Read the XLSX file using pandas
        df = pd.read_excel(input_xlsx)

        doc = SimpleDocTemplate(output_pdf, pagesize=letter)
        elements = []

        data = [list(df.columns)] + df.values.tolist()

        # Create a table from the data
        table = Table(data)

        elements.append(table)

        # Build the PDF document
        doc.build(elements)
        print(f"XLSX file converted to PDF: {output_pdf}")
    except Exception as e:
        print(f"Conversion failed: {str(e)}")
        
# Function to convert Word (DOCX) to PDF

def convert_docx_to_pdf(input_docx, output_pdf):
    try:
        word = win32com.client.Dispatch("Word.Application")
        doc = word.Documents.Open(os.path.abspath(input_docx))
        doc.SaveAs2(os.path.abspath(output_pdf), FileFormat=17)  # 17 represents PDF format
        doc.Close()
        word.Quit()
        print(f"DOCX file converted to PDF: {output_pdf}")
    except Exception as e:
        print(f"Conversion failed: {str(e)}")

# Main function
def main():
    parser = argparse.ArgumentParser(description="PDF Tools")
    parser.add_argument("input", help="Input file or folder")
    parser.add_argument("output_pdf", help="Output PDF file")

    args = parser.parse_args()
    input_path = args.input
    output_pdf = args.output_pdf

    if os.path.exists(input_path):
        if os.path.isfile(input_path):
            if input_path.lower().endswith(('.txt')):
                convert_text_to_pdf(input_path, output_pdf)
            elif input_path.lower().endswith(('.xlsx', '.xls')):
                convert_xlsx_to_pdf(input_path, output_pdf)
            elif input_path.lower().endswith(('.docx', '.doc')):
                convert_docx_to_pdf(input_path, output_pdf)
            else:
                convert_images_to_pdf(input_path, output_pdf)
        elif os.path.isdir(input_path):
            convert_images_to_pdf(input_path, output_pdf)
    else:
        print("Input not found or is not a valid file or folder.")

if __name__ == "__main__":
    main()