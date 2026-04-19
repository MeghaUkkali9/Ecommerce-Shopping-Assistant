import os
from shopping_assistant.utils.model_loader import ModelLoader
from langchain_astradb import AstraDBVectorStore
from langchain.retrievers.document_compressors import LLMChainFilter
from langchain.retrievers import ContextualCompressionRetriever

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
        """_summary_
        """
        if not self.vectore_store:
            collection_name = self.model_loader.config["astra_db"]["collection_name"]
            
            self.vectore_store =AstraDBVectorStore(
                embedding= self.model_loader.load_embeddings(),
                collection_name=collection_name,
                api_endpoint=self.astra_db_api_endpoint,
                token=self.astra_db_application_token,
                namespace=self.astra_db_keyspace,
                )
        if not self.retriever:
            top_k = self.model_loader.config["retriever"]["top_k"] if "retriever" in self.model_loader.config else 3
            
            mmr_retriever=self.vectore_store.as_retriever(
                search_type="mmr",
                search_kwargs={"k": top_k,
                                "fetch_k": 20,
                                "lambda_mult": 0.7,
                                "score_threshold": 0.6
                               })
            print("Retriever loaded successfully.")
            
            llm = self.model_loader.load_llm()
            
            compressor=LLMChainFilter.from_llm(llm)
            
            self.retriever = ContextualCompressionRetriever(
                base_compressor=compressor, 
                base_retriever=mmr_retriever
            )
            
        return self.retriever
            
    def retrieve(self, query):
        retriever = self.load_retriever()
        response = retriever.invoke(query)
        return response
        
        