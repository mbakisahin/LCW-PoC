from src.embedder.embedder import Embedder


class JobPostingEmbedder:
    """
    A class to handle the embedding of job postings.

    This class takes a job posting text, generates its embedding using the Embedder class,
    and provides access to the generated embedding.
    """

    def __init__(self, job_posting_text):
        """
        Initializes the JobPostingEmbedder with the provided job posting text.

        Args:
            job_posting_text (str): The text content of the job posting to be embedded.
        """
        self.embedder = Embedder()
        self.job_posting_text = job_posting_text
        self.job_embedding = self._embed_job_posting()

    def _embed_job_posting(self):
        """
        Generates an embedding for the job posting text.

        This method uses the Embedder class to create an embedding vector for the
        provided job posting text.

        Returns:
            list: The embedding vector representing the job posting.
        """
        # Embed the job posting and return the embedding vector
        return self.embedder.embed_text(self.job_posting_text)

    def get_job_embedding(self):
        """
        Retrieves the embedding vector of the job posting.

        Returns:
            list: The embedding vector of the job posting.
        """
        return self.job_embedding
