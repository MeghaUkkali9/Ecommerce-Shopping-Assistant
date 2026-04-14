import os
from dotenv import load_dotenv
from shopping_assistant.utils.model_loader import ModelLoader
from langchain_astradb import AstraDBVectorStore

class Retriever:
    def __init__(self):
        self.model_loader = ModelLoader()
        self.__load_env_variables()
        self.retriever = None
        self.vectore_store = None
        
    
    def __load_env_variables(self):
        required_vars = ["OPENAI_API_KEY", "ASTRA_DB_API_ENDPOINT", "ASTRA_DB_APPLICATION_TOKEN", "ASTRA_DB_KEYSPACE"]
        
        missing_vars = [variable for variable in required_vars if os.getenv(variable) is None]
        if missing_vars:
            raise EnvironmentError(f"Missing environment variables: {missing_vars}")
        
        self.openai_api_key = self.model_loader.api_key_mgr.get_openai_api_key()
        self.astra_db_api_endpoint = self.model_loader.api_key_mgr.get_astra_db_api_endpoint()
        self.astra_db_application_token = self.model_loader.api_key_mgr.get_astra_db_application_token()
        self.astra_db_keyspace = self.model_loader.api_key_mgr.get_astra_db_keyspace()    
    
    def __load_retriever(self):
        if self.vectore_store is None:
            self.vectore_store = AstraDBVectorStore(
                collection_name=self.model_loader.config["astra_db"]["collection_name"],
                embedding=self.model_loader.load_embeddings(),
                token=self.astra_db_application_token,
                api_endpoint=self.astra_db_api_endpoint,
                namespace=self.astra_db_keyspace,
            )
            
        if self.retriever is None:
            top_k = self.model_loader.config["retriever"]["top_k"] if "retriever" in self.model_loader.config and "top_k" in self.model_loader.config["retriever"] else 3
            self.retriever = self.vectore_store.as_retriever(search_kwargs={"k": top_k})
            return self.retriever
            
    def call_retriever(self, query):
        retriever = self.__load_retriever()
        response = retriever.invoke(query)
        return response
        
        