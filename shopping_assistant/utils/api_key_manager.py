import os
from shopping_assistant.logger import GLOBAL_LOGGER as log

class ApiKeyManager:
    def __init__(self):
        self.api_keys = {
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
            "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
            "ASTRA_DB_API_ENDPOINT": os.getenv("ASTRA_DB_API_ENDPOINT"),
            "ASTRA_DB_APPLICATION_TOKEN": os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
            "ASTRA_DB_KEYSPACE": os.getenv("ASTRA_DB_KEYSPACE"),
        }

    def get(self, key: str):
        return self.api_keys.get(key)
    
    def get_openai_api_key(self):
        return self.api_keys.get("OPENAI_API_KEY")
    
    def get_groq_api_key(self):
        return self.api_keys.get("GROQ_API_KEY")
    
    def get_astra_db_api_endpoint(self):
        return self.api_keys.get("ASTRA_DB_API_ENDPOINT")
    
    def get_astra_db_application_token(self):
        return self.api_keys.get("ASTRA_DB_APPLICATION_TOKEN")
    
    def get_astra_db_keyspace(self):
        return self.api_keys.get("ASTRA_DB_KEYSPACE")