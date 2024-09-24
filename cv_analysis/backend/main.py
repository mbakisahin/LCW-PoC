from fastapi import FastAPI, UploadFile, File, Form
from typing import List
from src.embedder.cv_embedder import CVEmbedder
from src.embedder.job_posting_embedder import JobPostingEmbedder
from utils.indexer import Indexer
from utils.search import AISearcher
import shutil
import os
import config
import tempfile  # Import tempfile module
import uuid      # Import uuid for unique identifiers

app = FastAPI()

def save_uploaded_file(uploaded_file: UploadFile, destination: str):
    """
    Saves an uploaded file to the specified destination path.

    Args:
        uploaded_file (UploadFile): The file uploaded by the user.
        destination (str): The file system path where the file will be saved.
    """
    with open(destination, "wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)

@app.post("/find-best-cv")
async def find_best_cvs(job_description: str = Form(...), cv_pdfs: List[UploadFile] = File(...)):
    """
    Processes the job description and uploaded CV PDFs to find the most suitable CVs.

    This endpoint performs the following steps:
        1. Embeds the job description using JobPostingEmbedder.
        2. Saves uploaded CV PDFs to a temporary directory.
        3. Embeds all CVs using CVEmbedder.
        4. Indexes the CV embeddings using Indexer.
        5. Searches for the most similar CVs using AISearcher.
        6. Deletes all indexed documents to clean up.
        7. Cleans up temporary files.

    Args:
        job_description (str): The text of the job description provided by the user.
        cv_pdfs (List[UploadFile]): A list of uploaded CV PDF files.

    Returns:
        dict: A dictionary containing a list of the best matching CVs' names, similarity scores, and contact information.
              If no suitable CVs are found, returns a message indicating so.
              In case of errors, returns an error message.
    """
    # Create a unique temporary directory for this request
    temp_dir = tempfile.mkdtemp(prefix="cv_uploads_")
    config.app_logger.info(f"Temporary directory created at {temp_dir}")

    try:
        # Embed the job description to obtain its embedding vector
        job_embedder = JobPostingEmbedder(job_description)
        job_embedding = job_embedder.get_job_embedding()

        # Save each uploaded PDF file to the temporary directory
        for pdf_file in cv_pdfs:
            # Ensure the filename is safe
            filename = os.path.basename(pdf_file.filename)
            file_path = os.path.join(temp_dir, filename)
            save_uploaded_file(pdf_file, file_path)
            config.app_logger.info(f"Saved uploaded file to {file_path}")

        # Embed all CVs by processing the saved PDF files
        cv_embedder = CVEmbedder(temp_dir)
        cv_embeddings = cv_embedder.embed_all_cvs()
        config.app_logger.info(f"Generated embeddings for {len(cv_embeddings)} CVs")

        # Initialize the Indexer and ingest the CV embeddings into Azure Cognitive Search
        indexer = Indexer(cv_embeddings)
        indexer.ingest_embeddings()
        config.app_logger.info("Embeddings ingested into the indexer")

        # Initialize the AISearcher and search for the most similar CVs based on the job embedding
        ai_searcher = AISearcher()
        similar_cvs = ai_searcher.search_similar_cv(job_embedding, top_k=10)  # Retrieve top 10 similar CVs
        config.app_logger.info(f"Search completed, found {len(similar_cvs)} similar CV(s).")

        # Delete all indexed documents to clean up the search index
        indexer.delete_all_documents()
        config.app_logger.info("Indexed data deleted.")

        if similar_cvs:
            # Prepare the list of CVs to return
            cv_list = []
            for cv in similar_cvs:
                cv_info = {
                    "cv_name": cv['cv_name'],
                    "similarity_score": cv['similarity_score'],
                    "contact_info": cv.get('contact_info', "No contact info available")
                }
                cv_list.append(cv_info)
            config.app_logger.info(f"Returning {len(cv_list)} CVs.")
            return {"cv_list": cv_list}
        else:
            config.app_logger.info("No suitable CVs found.")
            return {"message": "No suitable CVs found."}

    except Exception as e:
        config.app_logger.error(f"An error occurred: {str(e)}")
        return {"error": str(e)}

    finally:
        # Clean up temporary files
        shutil.rmtree(temp_dir)
        config.app_logger.info(f"Temporary directory {temp_dir} deleted.")

# Run the FastAPI application using Uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
