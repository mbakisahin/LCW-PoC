import os
import PyPDF2


class PDFProcessor:
    """
    A class to handle the extraction of text from PDF files in a specified folder.

    This class provides methods to extract text from individual PDF files as well as
    to process all PDF files within a given directory.
    """

    def __init__(self, pdf_folder_path):
        """
        Initializes the PDFProcessor with the path to the PDF folder.

        Args:
            pdf_folder_path (str): The path to the folder containing PDF files.
        """
        self.pdf_folder_path = pdf_folder_path

    def extract_text_from_pdf(self, pdf_file):
        """
        Extracts text from a single PDF file.

        This method attempts to read and extract text from each page of the specified PDF file
        using PyPDF2. If an error occurs during the process, it catches the exception,
        prints an error message, and returns None.

        Args:
            pdf_file (str): The path to the PDF file from which to extract text.

        Returns:
            str or None: The extracted text from the PDF if successful; otherwise, None.
        """
        try:
            with open(pdf_file, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ''
                # Iterate through each page in the PDF and extract text
                for page_num in range(len(reader.pages)):
                    page_text = reader.pages[page_num].extract_text()
                    if page_text:
                        text += page_text
                return text
        except Exception as e:
            print(f"Error reading {pdf_file}: {e}")
            return None

    def extract_texts_from_all_pdfs(self):
        """
        Extracts text from all PDF files in the specified folder.

        This method scans the PDF folder for files with a `.pdf` extension, extracts text
        from each valid PDF file using the `extract_text_from_pdf` method, and aggregates
        the results into a dictionary.

        Returns:
            dict: A dictionary where each key is the PDF filename and the value is the
                  extracted text content of that PDF.
        """
        pdf_texts = {}
        # Iterate through all files in the PDF folder
        for filename in os.listdir(self.pdf_folder_path):
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(self.pdf_folder_path, filename)
                text = self.extract_text_from_pdf(pdf_path)
                if text:
                    pdf_texts[filename] = text
        return pdf_texts
