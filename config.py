import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    MODEL_NAME = os.getenv('MODEL_NAME', 'perplexity/llama-3.1-sonar-large-128k-online')
