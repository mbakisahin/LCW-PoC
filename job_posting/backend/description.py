from utils.openAI import OpenAIClient
from utils.system_messages import SYSTEM_MESSAGES_DESCRIPTION
import config


class JobDescriptionGenerator:
    """
    A class to generate job descriptions based on provided qualifications and role definitions.

    This class utilizes the OpenAIClient to interact with OpenAI's API, generating comprehensive
    job descriptions by comparing and synthesizing the given qualifications and role definitions.
    It also provides functionality to save the generated job descriptions to a file.
    """

    def __init__(self):
        """
        Initializes the JobDescriptionGenerator by creating an instance of OpenAIClient.

        The OpenAIClient is configured with the specified engine to handle API interactions.
        """
        # Initialize the OpenAIClient with the specified engine
        client = OpenAIClient(engine="gpt-4o")
        self.openai_client = client

    def generate_job_description(self, qualifications, role_definition):
        """
        Generates a job description based on provided qualifications and role definitions.

        This method formats the input qualifications and role definitions, sends them to the
        OpenAI API via the OpenAIClient, and retrieves a comprehensive job description.

        Args:
            qualifications (list of str): A list of qualifications required for the job.
            role_definition (list of str): A list of role definitions outlining the job responsibilities.

        Returns:
            str: The generated job description if successful.
                 Returns an error message string if an exception occurs.
        """
        config.app_logger.info("Generating job description based on Qualifications and Role Definition.")

        # Format the input text for the OpenAI API
        input_text = (
            f"Qualifications: {', '.join(qualifications)}\n"
            f"Role Definition: {', '.join(role_definition)}"
        )

        # Send the formatted input to the OpenAI API to generate the job description
        try:
            job_description = self.openai_client.compare_texts(input_text, SYSTEM_MESSAGES_DESCRIPTION)
            config.app_logger.info("Job description successfully generated.")
            return job_description
        except Exception as e:
            config.app_logger.error(f"Error generating job description: {str(e)}")
            return f"Error generating job description: {str(e)}"

    def save_job_description_to_file(self, job_description, file_path):
        """
        Saves the generated job description to a specified file.

        This method writes the provided job description string to a file at the given file path.

        Args:
            job_description (str): The job description text to be saved.
            file_path (str): The file system path where the job description will be saved.

        Returns:
            None
        """
        try:
            with open(file_path, 'w') as file:
                file.write(job_description)
            config.app_logger.info(f"Job description successfully saved to {file_path}")
        except Exception as e:
            config.app_logger.error(f"Error saving job description to file: {str(e)}")
