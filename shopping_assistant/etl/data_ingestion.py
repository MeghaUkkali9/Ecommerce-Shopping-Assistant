import os
import re
import pandas as pd
from dotenv import load_dotenv
from typing import List
from langchain_core.documents import Document
from langchain_astradb import AstraDBVectorStore

from shopping_assistant.utils.config_loader import load_config
from shopping_assistant.utils.model_loader import ModelLoader
from shopping_assistant.exception.custom_exception import ProductAssistantException


class DataIngestion:
    """
    Data ingestion pipeline:
    CSV → Clean → Split Reviews → Documents → Vector DB
    """

    def __init__(self):
        print("Initializing DataIngestion pipeline...")

        self.model_loader = ModelLoader()
        self.__load_env_variables()
        self.csv_path = self.__get_csv_path()
        self.product_data = self.__load_csv()
        self.config = load_config()

    def __load_env_variables(self):
        load_dotenv()

        required_vars = [
            "OPENAI_API_KEY",
            "ASTRA_DB_API_ENDPOINT",
            "ASTRA_DB_APPLICATION_TOKEN",
            "ASTRA_DB_KEYSPACE",
        ]

        missing_vars = [var for var in required_vars if os.getenv(var) is None]
        if missing_vars:
            raise EnvironmentError(f"Missing environment variables: {missing_vars}")

        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.db_api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")
        self.db_application_token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
        self.db_keyspace = os.getenv("ASTRA_DB_KEYSPACE")

    def __get_csv_path(self):
        """
        Get the path to the CSV file containing product reviews.
        """
        current_dir = os.getcwd()
        csv_path = os.path.join(current_dir, 'data', 'product_reviews.csv')

        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found at: {csv_path}")

        return csv_path
    
    def __load_csv(self):
        """
        Load the CSV file into a pandas DataFrame.
        """
        df = pd.read_csv(self.csv_path)

        expected_columns = {
            "product_id",
            "product_title",
            "rating",
            "total_reviews",
            "price",
            "top_reviews",
        }

        if not expected_columns.issubset(set(df.columns)):
            raise ValueError(f"CSV must contain columns: {expected_columns}")

        return df

    def __clean_review(self, text: str) -> str:
        if not text:
            return ""

        # remove emojis only
        text = re.sub(r"[\U0001F300-\U0001FAFF]+", "", text)

        # fix punctuation spacing
        text = re.sub(r"\s+([.,!?])", r"\1", text)

        # normalize spaces
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def transform_data_to_documents(self) -> List[Document]:
        try:
            if self.product_data is None or self.product_data.empty:
                raise ProductAssistantException("CSV data is empty.")

            documents = []

            for row in self.product_data.to_dict(orient="records"):

                metadata = {
                    "product_id": row.get("product_id"),
                    "product_title": row.get("product_title"),
                    "rating": self.safe_float(row.get("rating")),
                    "total_reviews": self.safe_int(row.get("total_reviews")),
                    "price": self.safe_price(row.get("price")),
                }

                # SPLIT REVIEWS
                raw_reviews = str(row.get("top_reviews", "")).split("||")

                for review in raw_reviews:
                    review = self.__clean_review(review.strip())

                    if not review or review.lower() == "no reviews found":
                        continue

                    doc = Document(
                        page_content=review,
                        metadata=metadata
                    )

                    documents.append(doc)

            if not documents:
                raise ProductAssistantException("No valid documents created.")

            print(f"Transformed {len(documents)} documents.")

            return documents

        except Exception as e:
            raise ProductAssistantException(f"Transformation error: {str(e)}")

    def store_in_vector_db(self, documents: List[Document]):
        collection_name = self.config["astra_db"]["collection_name"]

        vstore = AstraDBVectorStore(
            embedding=self.model_loader.load_embeddings(),
            collection_name=collection_name,
            api_endpoint=self.db_api_endpoint,
            token=self.db_application_token,
            namespace=self.db_keyspace,
        )

        # batch insert (scalable)
        batch_size = 100
        all_ids = []

        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            ids = vstore.add_documents(batch)
            all_ids.extend(ids)

        print(f"Inserted {len(all_ids)} documents into AstraDB.")

        return vstore, all_ids

    def run_pipeline(self):
        try:
            documents = self.transform_data_to_documents()
            vstore, _ = self.store_in_vector_db(documents)

            # better query
            query = "best lipstick for dry lips under 1000"
            results = vstore.similarity_search(query)

            print(f"\nSample search results for: '{query}'\n")

            for res in results:
                print(f"{res.page_content}")
                print(f"{res.metadata}\n")

        except FileNotFoundError as fe:
            raise ProductAssistantException(f"CSV error: {fe}")

        except Exception as e:
            raise ProductAssistantException(f"Pipeline failed: {str(e)}")

    def safe_int(self, value, default=0):
        try:
            if isinstance(value, str):
                value = value.replace(",", "").strip()
            return int(value)
        except:
            return default

    def safe_float(self, value, default=0.0):
        try:
            if isinstance(value, str):
                value = value.replace(",", "").strip()
                value = value.split()[0]
            return float(value)
        except:
            return default

    def safe_price(self, value, default=0):
        try:
            if isinstance(value, str):
                value = value.replace("₹", "").replace(",", "").strip()
            return float(value)
        except:
            return default

if __name__ == "__main__":
    ingestion = DataIngestion()
    ingestion.run_pipeline()