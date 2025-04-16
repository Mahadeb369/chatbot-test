import os
import json
from dotenv import load_dotenv
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE_URI = os.getenv('DATABASE_URI') or ""

class Config():
    DEBUG = False

class LocalDevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    if DATABASE_URI and DATABASE_URI != "":
        SQLALCHEMY_DATABASE_URI = DATABASE_URI
    else:
        raise ValueError("DATABASE_URI is not set. Please provide a valid database URL.")

# Define the API keys
class APIConfig():
    # OPENAI_API_KEY = data['OPENAI_API_KEY']
    OPENAI_API_KEY = os.getenv("OPEN_AI_API_KEY") or ""

    llm_config = {
        'model': 'gpt-4o-mini',
        'api_key': OPENAI_API_KEY,
        'api_type': 'openai',
    }

    llm_config_advanced = {
        'model': 'gpt-4o-2024-08-06',
        # 'model': 'gpt-4o-mini',
        'api_key': OPENAI_API_KEY,
        'api_type': 'openai',
    }