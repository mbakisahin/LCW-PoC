from fastapi import FastAPI
from pydantic import BaseModel
from description import JobDescriptionGenerator
import config

app = FastAPI()


class JobDescriptionRequest(BaseModel):
    """
    Pydantic model representing the structure of the job description generation request.

    Attributes:
        qualifications (str): A comma-separated string of qualifications required for the job.
        role_definition (str): A comma-separated string of role definitions outlining the job responsibilities.
    """
    qualifications: str  # Qualifications provided by the user, comma-separated
    role_definition: str  # Role definitions provided by the user, comma-separated


@app.post("/generate_job_description")
def generate_job_description(request: JobDescriptionRequest):
    """
    Generates a job description based on provided qualifications and role definitions.

    This endpoint receives a POST request with qualifications and role definitions,
    processes the inputs to generate a comprehensive job description using the
    JobDescriptionGenerator, and returns the generated description.

    Args:
        request (JobDescriptionRequest): The request payload containing qualifications and role definitions.

    Returns:
        dict: A dictionary containing the generated job description.
              Example:
              {
                  "job_description": "Generated job description text..."
              }
    """
    config.app_logger.info("Generating job description from request data.")

    # Initialize the JobDescriptionGenerator
    generator = JobDescriptionGenerator()

    # Split the comma-separated strings into lists
    qualifications_list = [qual.strip() for qual in request.qualifications.split(",") if qual.strip()]
    role_definition_list = [role.strip() for role in request.role_definition.split(",") if role.strip()]

    # Generate the job description using the provided qualifications and role definitions
    job_description = generator.generate_job_description(
        qualifications_list,
        role_definition_list
    )

    return {"job_description": job_description}


# Entry point to run the FastAPI application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
