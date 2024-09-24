class JobPostingProcessor:
    """
    A class to handle the loading and processing of job posting files.

    This class reads a job posting from a specified file and provides access to its text content.
    """

    def __init__(self, job_posting_file):
        """
        Initializes the JobPostingProcessor with the path to the job posting file.

        Args:
            job_posting_file (str): The path to the file containing the job posting.
        """
        self.job_posting_file = job_posting_file
        self.job_posting_text = self._load_job_posting()

    def _load_job_posting(self):
        """
        Loads the job posting text from the specified file.

        Attempts to open and read the content of the job posting file. If an error occurs
        during the file operation, it catches the exception, prints an error message,
        and returns None.

        Returns:
            str or None: The text content of the job posting if successful; otherwise, None.
        """
        try:
            with open(self.job_posting_file, 'r') as file:
                return file.read()
        except Exception as e:
            print(f"Error loading job posting: {e}")
            return None

    def get_job_posting_text(self):
        """
        Retrieves the loaded job posting text.

        Returns:
            str or None: The text content of the job posting if it was successfully loaded; otherwise, None.
        """
        return self.job_posting_text
