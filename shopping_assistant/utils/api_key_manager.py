import os
from dotenv import load_dotenv
from shopping_assistant.logger import GLOBAL_LOGGER as log

class ApiKeyManager:
    def __init__(self):
        load_dotenv() 
        log.info("Environment variables loaded")

    def get(self, key: str):
        value = os.getenv(key)

        if value is None:
            log.error(f"Missing API key: {key}")
            raise EnvironmentError(f"Missing API key: {key}")

        return value
    
    def get_openai_api_key(self):
        return self.get("OPENAI_API_KEY")
    
    def get_groq_api_key(self):
        return self.get("GROQ_API_KEY")
    
    def get_astra_db_api_endpoint(self):
        return self.get("ASTRA_DB_API_ENDPOINT")
    
    def get_astra_db_application_token(self):
        return self.get("ASTRA_DB_APPLICATION_TOKEN")
    
    def get_astra_db_keyspace(self):
        return self.get("ASTRA_DB_KEYSPACE")