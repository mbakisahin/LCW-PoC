from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from uuid import uuid4
from azure.search.documents.indexes.models import (
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchIndex,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
)
import config


class Indexer:
    """
    A class to handle the indexing of CV embeddings into Azure Cognitive Search.

    This class manages the creation of search indexes, preparation of documents,
    ingestion of embeddings, and verification of document indexing within Azure Cognitive Search.
    """

    def __init__(self, cv_embeddings):
        """
        Initializes the Indexer with CV embeddings and sets up Azure Search clients.

        Args:
            cv_embeddings (dict): A dictionary containing CV embeddings with CV names as keys.
        """
        self.cv_embeddings = cv_embeddings
        self.index_client = SearchIndexClient(
            endpoint=config.COGNITIVE_SEARCH_CONFIG["endpoint"],
            credential=AzureKeyCredential(config.COGNITIVE_SEARCH_CONFIG["api_key"])
        )
        self.search_client = SearchClient(
            endpoint=config.COGNITIVE_SEARCH_CONFIG["endpoint"],
            index_name=config.COGNITIVE_SEARCH_CONFIG["index_name"],
            credential=AzureKeyCredential(config.COGNITIVE_SEARCH_CONFIG["api_key"])
        )

    def does_index_exist(self):
        """
        Checks if the specified search index exists in Azure Cognitive Search.

        Returns:
            bool: True if the index exists, False otherwise.
        """
        try:
            index_names = list(self.index_client.list_index_names())
            return config.COGNITIVE_SEARCH_CONFIG["index_name"] in index_names
        except Exception as e:
            config.app_logger.error(f"Error checking index existence: {str(e)}")
            return False

    def create_index(self):
        """
        Creates a search index in Azure Cognitive Search if it does not already exist.

        The index includes fields for CV ID, name, embedding vector, and contact information.
        It also configures vector search capabilities using the HNSW algorithm.
        """
        if not self.does_index_exist():
            try:
                fields = [
                    SimpleField(
                        name="id",
                        type=SearchFieldDataType.String,
                        key=True,
                        filterable=True,
                        sortable=True
                    ),
                    SearchableField(
                        name="cv_name",
                        type=SearchFieldDataType.String,
                        searchable=True,
                        filterable=True,
                        sortable=True
                    ),
                    SearchField(
                        name="cv_vector",
                        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                        searchable=True,
                        vector_search_dimensions=config.EMBEDDING_DIMENSION,
                        vector_search_profile_name="default_vector_search_profile",
                    ),
                    SearchableField(
                        name="contact_info",
                        type=SearchFieldDataType.String,
                        searchable=True
                    )
                ]

                search_index = SearchIndex(
                    name=config.COGNITIVE_SEARCH_CONFIG["index_name"],
                    fields=fields,
                    vector_search=VectorSearch(
                        profiles=[
                            VectorSearchProfile(
                                name="default_vector_search_profile",
                                algorithm_configuration_name="default_hnsw_algorithm_config"
                            )
                        ],
                        algorithms=[
                            HnswAlgorithmConfiguration(
                                name="default_hnsw_algorithm_config",
                            )
                        ]
                    )
                )
                self.index_client.create_index(search_index)
                config.app_logger.info("Search Index is created successfully!")
            except Exception as e:
                config.app_logger.error(f"Error creating index: {str(e)}")
        else:
            config.app_logger.info("Index already exists. Skipping index creation.")

    def prepare_document(self, cv_name, embedding, contact_info):
        """
        Prepares a document dictionary for indexing into Azure Cognitive Search.

        Args:
            cv_name (str): The name of the CV file.
            embedding (list): The embedding vector representing the CV.
            contact_info (str): The extracted contact information from the CV.

        Returns:
            dict or None: A dictionary representing the document ready for indexing,
                          or None if an error occurs.
        """
        try:
            if len(embedding) != config.EMBEDDING_DIMENSION:
                raise ValueError(
                    f"Embedding dimension mismatch: Expected {config.EMBEDDING_DIMENSION}, got {len(embedding)}"
                )

            document = {
                "id": str(uuid4()),
                "cv_name": cv_name,
                "cv_vector": embedding,
                "contact_info": contact_info
            }
            return document
        except Exception as e:
            config.app_logger.error(f"Error preparing document for {cv_name}: {str(e)}")
            return None

    def ingest_embeddings(self):
        """
        Ingests all CV embeddings into Azure Cognitive Search.

        This method performs the following steps:
            1. Creates the search index if it does not exist.
            2. Iterates through all CV embeddings.
            3. Checks if each CV is already indexed.
            4. Prepares and uploads new documents to the search index.

        Logs the outcome of the ingestion process.
        """
        # Create the index if it does not exist
        self.create_index()

        documents = []
        for cv_name, cv_data in self.cv_embeddings.items():
            cv_embedding = cv_data['embedding']
            contact_info = cv_data.get('contact_info', '')

            # Check if the CV is already indexed
            if not self.is_document_indexed(cv_name):
                document = self.prepare_document(cv_name, cv_embedding, contact_info)
                if document:
                    documents.append(document)

        if documents:
            try:
                self.search_client.upload_documents(documents=documents)
                config.app_logger.info(f"{len(documents)} documents indexed successfully!")
            except Exception as e:
                config.app_logger.error(f"Error during document ingestion: {str(e)}")
        else:
            config.app_logger.info("No new documents to index.")

    def is_document_indexed(self, cv_name):
        """
        Checks if a document with the given CV name is already indexed in Azure Cognitive Search.

        Args:
            cv_name (str): The name of the CV file to check.

        Returns:
            bool: True if the document is indexed, False otherwise.
        """
        try:
            results = self.search_client.search(
                search_text="*",
                filter=f"cv_name eq '{cv_name}'",
                include_total_count=True
            )
            return results.get_count() > 0
        except Exception as e:
            config.app_logger.error(f"Error checking if document is indexed: {str(e)}")
            return False

    def delete_all_documents(self):
        """
        Deletes the entire search index and recreates it to remove all documents.

        This effectively clears all indexed data by removing the index and setting it up anew.
        """
        try:
            # Delete the existing index
            self.index_client.delete_index(config.COGNITIVE_SEARCH_CONFIG["index_name"])
            config.app_logger.info(
                f"Search index '{config.COGNITIVE_SEARCH_CONFIG['index_name']}' deleted successfully."
            )

            # Recreate the index
            self.create_index()
        except Exception as e:
            config.app_logger.error(f"Error during index deletion and recreation: {str(e)}")
