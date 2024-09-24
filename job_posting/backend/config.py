import os
import logging
from dotenv import load_dotenv
import openai
import tiktoken

load_dotenv()


AZURE_OPENAI_CONFIG = {
    'api_key': os.getenv('AZURE_OPENAI_API_KEY'),
    'api_base': os.getenv('AZURE_OPENAI_API_BASE'),
    'deployment_name': os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
    'api_version': "2023-05-15"
}


openai.api_type = "azure"
openai.api_key = AZURE_OPENAI_CONFIG['api_key']
openai.api_base = AZURE_OPENAI_CONFIG['api_base']
openai.api_version = AZURE_OPENAI_CONFIG['api_version']

encoding = tiktoken.encoding_for_model("gpt-4o")

PORT = "8000"
HOST = "0.0.0.0"
CONCURRENCY_LIMIT = 50

# Logging Configuration
logger = logging.getLogger('PoC')
formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s', "%Y-%m-%d %H:%M:%S")

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)
app_logger = logger
