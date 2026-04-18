import os
from shopping_assistant.utils.model_loader import ModelLoader
from langchain_astradb import AstraDBVectorStore

class Retriever:
    def __init__(self):
        self.model_loader = ModelLoader()
        self.__load_env_variables()
        self.retriever = None
        self.vectore_store = None
        
    def __load_env_variables(self):
        api_key_mgr = self.model_loader.api_key_mgr

        self.openai_api_key = api_key_mgr.get_openai_api_key()
        self.astra_db_api_endpoint = api_key_mgr.get_astra_db_api_endpoint()
        self.astra_db_application_token = api_key_mgr.get_astra_db_application_token()
        self.astra_db_keyspace = api_key_mgr.get_astra_db_keyspace() 
    
    def load_retriever(self):
        if self.vectore_store is None:
            self.vectore_store = AstraDBVectorStore(
                collection_name=self.model_loader.config["astra_db"]["collection_name"],
                embedding=self.model_loader.load_embeddings(),
                token=self.astra_db_application_token,
                api_endpoint=self.astra_db_api_endpoint,
                namespace=self.astra_db_keyspace,
            )
            
        if self.retriever is None:
            config = self.model_loader.config
            top_k = self.model_loader.config["retriever"]["top_k"] if "retriever" in config and "top_k" in config["retriever"] else 3
            self.retriever = self.vectore_store.as_retriever(search_kwargs={"k": top_k})
            
        return self.retriever
            
    def retrieve(self, query):
        retriever = self.load_retriever()
        response = retriever.invoke(query)
        return response
        
        