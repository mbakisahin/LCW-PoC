from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
import config


class AISearcher:
    """
    A class to handle searching for similar CVs using Azure Cognitive Search.

    This class connects to an Azure Cognitive Search index containing CV embeddings and provides
    functionality to search for the most similar CVs based on a provided job embedding vector.
    """

    def __init__(self):
        """
        Initializes the AISearcher by setting up the Azure SearchClient.

        The SearchClient is configured using the endpoint, index name, and API key provided
        in the configuration.
        """
        self.search_client = SearchClient(
            endpoint=config.COGNITIVE_SEARCH_CONFIG["endpoint"],
            index_name=config.COGNITIVE_SEARCH_CONFIG["index_name"],
            credential=AzureKeyCredential(config.COGNITIVE_SEARCH_CONFIG["api_key"])
        )

    def search_similar_cv(self, job_embedding, top_k=10):
        """
        Searches for the most similar CVs based on the provided job embedding.

        This method performs a vector search against the "cv_vector" field in the Azure Cognitive Search index.
        It retrieves the top_k CVs that are closest to the provided job embedding vector.

        Args:
            job_embedding (list): The embedding vector for the job description.
            top_k (int, optional): The number of top similar CVs to return. Defaults to 3.

        Returns:
            list: A list of dictionaries, each containing the CV name, contact information, and similarity score.
                  Returns an empty list if an error occurs during the search.
        """
        try:
            # Create a VectorizedQuery to search for similar vectors in the "cv_vector" field
            vector_query = VectorizedQuery(
                vector=job_embedding,
                k_nearest_neighbors=top_k,
                fields="cv_vector",
                exhaustive=True  # Set to True for exact nearest neighbor search
            )

            # Perform the search on the indexed CV vectors
            search_results = self.search_client.search(
                search_text="*",  # Wildcard to include all documents, prioritize vector search
                vector_queries=[vector_query],
                select=["cv_name", "contact_info"],  # Include contact_info in the results
                top=top_k
            )

            # Process the search results and compile the top CVs with their similarity scores and contact information
            results = []
            for result in search_results:
                results.append({
                    "cv_name": result["cv_name"],
                    "contact_info": result.get("contact_info", "N/A"),  # Default to "N/A" if contact_info is missing
                    "similarity_score": result["@search.score"]  # Retrieve the similarity score from the search metadata
                })

            return results

        except Exception as e:
            # Log any exceptions that occur during the search process
            config.app_logger.error(f"Error during search for similar CVs: {str(e)}")
            return []
