import os, pandas as pd
from dotenv import load_dotenv
from typing import List, Dict
from langchain_core.documents import Document
from langchain_astradb import AstraDBVectorStore
from shopping_assistant.utils.config_loader import load_config
from shopping_assistant.utils.model_loader import ModelLoader

class DataIngestion:
    """
    This class is responsible for ingesting data into the vector database.
    It loads product reviews from a CSV file,
    """

    def __init__(self):
        print("Initializing DataIngestion pipeline...")
        self.model_loader=ModelLoader()
        self.__load_env_variables()
        self.csv_path = self.__get_csv_path()
        self.product_data = self.__load_csv()
        self.config=load_config()
    
    def __load_env_variables(self):
        """
        Load environment variables from .env file.
        """
        load_dotenv()
        
        required_vars = ["GOOGLE_API_KEY", "ASTRA_DB_API_ENDPOINT", "ASTRA_DB_APPLICATION_TOKEN", "ASTRA_DB_KEYSPACE"]
        
        missing_vars = [var for var in required_vars if os.getenv(var) is None]
        if missing_vars:
            raise EnvironmentError(f"Missing environment variables: {missing_vars}")
        
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.db_api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")
        self.db_application_token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
        self.db_keyspace = os.getenv("ASTRA_DB_KEYSPACE")
    
    def __get_csv_path(self):
        """
        Get the path to the CSV file containing product reviews.
        """
        current_dir = os.getcwd()
        csv_path = os.path.join(current_dir,'data', 'product_reviews.csv')

        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found at: {csv_path}")

        return csv_path
    
    def __load_csv(self):
        """
        Load the CSV file into a pandas DataFrame.
        """
        df = pd.read_csv(self.csv_path)
        expected_columns = {'product_id','product_title', 'rating', 'total_reviews','price', 'top_reviews'}

        if not expected_columns.issubset(set(df.columns)):
            raise ValueError(f"CSV must contain columns: {expected_columns}")

        return df
    
    def tranform_data_to_documents(self):
        """
        Transform the DataFrame into a list of Document objects for embedding.
         Each Document should contain the review text and metadata (e.g., product name, rating).
         This will be used for generating embeddings and storing in the vector database.
         The metadata can be stored in the 'metadata' field of the Document object as a dictionary.
         For example:
         Document(
             page_content="This is a great product!",
             metadata={
                 "product_name": "Example Product",
                 "rating": 5,
                 "price": "$19.99"
             }
         )
         """
        product_list = []

        for _, row in self.product_data.iterrows():
            product_entry = {
                    "product_id": row["product_id"],
                    "product_title": row["product_title"],
                    "rating": row["rating"],
                    "total_reviews": row["total_reviews"],
                    "price": row["price"],
                    "top_reviews": row["top_reviews"]
                }
            product_list.append(product_entry)

        documents = []
        for entry in product_list:
            metadata = {
                    "product_id": entry["product_id"],
                    "product_title": entry["product_title"],
                    "rating": entry["rating"],
                    "total_reviews": entry["total_reviews"],
                    "price": entry["price"]
            }
            doc = Document(page_content=entry["top_reviews"], metadata=metadata)
            documents.append(doc)

        print(f"Transformed {len(documents)} documents.")
        return documents
    
    def store_in_vector_db(self, documents: List[Document]):
        """
        Store the list of Document objects in the AstraDB vector database.
         This involves generating embeddings for each Document and then upserting them into the database.
         Use the ModelLoader class to load the embedding model and generate embeddings for the documents.
         The AstraDBVectorStore class can be used to interact with the AstraDB vector database.
        """
        collection_name=self.config["astra_db"]["collection_name"]
        vstore = AstraDBVectorStore(
            embedding= self.model_loader.load_embeddings(),
            collection_name=collection_name,
            api_endpoint=self.db_api_endpoint,
            token=self.db_application_token,
            namespace=self.db_keyspace,
        )

        inserted_ids = vstore.add_documents(documents)
        print(f"Successfully inserted {len(inserted_ids)} documents into AstraDB.")
        return vstore, inserted_ids
    
    def run_pipline(self):
        """
        Run the entire data ingestion pipeline:
         1. Load environment variables
         2. Load CSV data
         3. Transform data into Document objects
         4. Store in vector database
         This method orchestrates the entire process and can be called to execute the data ingestion.
         It should handle any exceptions that occur during the process and log appropriate messages.
         For example, if the CSV file is not found, it should log an error message and exit gracefully.
         If the data is successfully ingested, it should log a success message with the number of documents ingested.
        """
        documents = self.transform_data()
        vstore, _ = self.store_in_vector_db(documents)

        #Optionally do a quick search
        query = "Can you tell me the low budget iphone?"
        results = vstore.similarity_search(query)

        print(f"\nSample search results for query: '{query}'")
        for res in results:
            print(f"Content: {res.page_content}\nMetadata: {res.metadata}\n")

# Run if this file is executed directly
if __name__ == "__main__":
    ingestion = DataIngestion()
    ingestion.run_pipeline()
    
