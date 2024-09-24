import re
from src.embedder.embedder import Embedder
from src.processors.pdf_processor import PDFProcessor

from utils.openAI import OpenAIClient


class CVEmbedder:
    """
    A class to handle the embedding of CVs from a specified folder.

    This class extracts text from PDF CVs, removes contact information using OpenAI,
    and generates embeddings for the cleaned CV text.
    """

    def __init__(self, cv_folder_path):
        """
        Initializes the CVEmbedder with the path to the CV folder.

        Args:
            cv_folder_path (str): The path to the folder containing CV PDFs.
        """
        self.cv_folder_path = cv_folder_path
        self.embedder = Embedder()
        self.openai_client = OpenAIClient(engine="gpt-4o")

    def embed_all_cvs(self):
        """
        Processes and embeds all CVs in the specified folder.

        For each CV:
            1. Extracts contact information using OpenAI.
            2. Removes the contact information from the CV text.
            3. Generates an embedding for the cleaned CV text.
            4. Stores the embedding along with the CV name and contact information.

        Returns:
            dict: A dictionary where each key is the CV name and the value is another
                  dictionary containing the CV name, its embedding, and contact information.
        """
        cv_embeddings = {}
        for cv_name, cv_text in self._get_all_cv_texts().items():
            # Extract contact information from the CV text
            contact_info = self.openai_client.extract_contact_info(cv_text)
            # Remove contact information from the CV text
            cv_text_without_contact = cv_text.replace(contact_info, "")

            # Generate embedding for the cleaned CV text
            embedding = self.embedder.embed_text(cv_text_without_contact)
            if embedding:
                # Add contact information after embedding
                cv_embeddings[cv_name] = {
                    "cv_name": cv_name,
                    "embedding": embedding,
                    "contact_info": contact_info,  # Add contact information
                }
        return cv_embeddings

    def _get_all_cv_texts(self):
        """
        Extracts and cleans text from all PDF CVs in the specified folder using GPT-4.

        For each PDF CV:
            1. Extracts raw text using PDFProcessor.
            2. Cleans the extracted text using OpenAI's GPT-4.

        Returns:
            dict: A dictionary where each key is the CV name and the value is the cleaned text.
        """
        cv_texts = {}
        pdf_processor = PDFProcessor(self.cv_folder_path)
        # Extract raw text from all PDFs
        for cv_name, raw_pdf_text in pdf_processor.extract_texts_from_all_pdfs().items():
            # Clean the extracted text using GPT-4
            clean_text = self.openai_client.extract_text_using_gpt(raw_pdf_text)
            cv_texts[cv_name] = clean_text
        return cv_texts
