import logging
import os
import pickle

import openai
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from api_template.config.settings import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class SemanticSearch:
    def __init__(
        self,
        cache_file="embeddings_cache.pkl",
        cache_path=None,
        collection_name="local_embeddings",
        vector_size=1536,
    ):
        self.cache_path = os.path.join(os.path.dirname(__file__), "../data")
        if cache_path:
            self.cache_path = cache_path

        self.path = os.path.join(os.path.dirname(__file__), f"{self.cache_path}/{collection_name}")
        self.client = QdrantClient(path=self.path)
        self.cache_file = cache_file
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.embeddings_cache = self._load_cache()
        self._initialize_qdrant()

    def _initialize_qdrant(self):
        """
        Initializes Qdrant with the collection name and vector size.
        :return:
        """
        logger.info("Initializing Qdrant...")
        if not self.client.collection_exists(self.collection_name):
            logger.info("Creating collection...")
            self.client.create_collection(
                self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE,
                ),
            )

    def _load_cache(self):
        """
        Load embeddings cache from a Pickle file.
        :return:
        """
        cache_file_path = f"{self.cache_path}/{self.cache_file}"
        if os.path.exists(cache_file_path):
            logger.info(f"Loading embeddings cache from {cache_file_path}")
            with open(cache_file_path, "rb") as f:
                return pickle.load(f)
        else:
            logger.info("No cache found, creating new cache.")
            return {}

    def _save_cache(self):
        """
        Save embeddings cache to a Pickle file.
        :return:
        """
        cache_file_path = f"{self.cache_path}/{self.cache_file}"
        logger.info(f"Saving embeddings cache to {cache_file_path}...")
        with open(cache_file_path, "wb") as f:
            pickle.dump(self.embeddings_cache, f)

    def _calculate_embeddings(self, texts):
        """
        Calculates embeddings for a list of texts.
        :param texts:
        :return:
        """
        logger.info("Calculating embeddings...")
        client = openai.Client(api_key=settings.OPENAI_API_KEY)
        response = client.embeddings.create(input=texts, model="text-embedding-3-small")
        return response.data

    def index_specs(self, specs):
        """
        Indexes the descriptions of the APIs in the semantic search engine.
        :param specs:
        :return:
        """
        logger.info("Indexing API descriptions...")
        points = []

        for idx, (path, description) in enumerate(specs.items()):
            logger.info(f"Indexing API {idx}. {path} - {description}...")
            if path not in self.embeddings_cache:
                embedding = self._calculate_embeddings([description])
                embedding = embedding[0]
                logger.info(f"Embedding for {path}: {embedding}")
                self.embeddings_cache[path] = embedding.embedding

            points.append(
                PointStruct(id=idx, vector=self.embeddings_cache[path], payload={"path": path})
            )

        self._save_cache()
        self.client.upsert(self.collection_name, points)

    def search(self, query):
        """
        Searches for APIs with a semantic query.
        :param query: Search query.
        :return: List of search results.
        """
        logger.info(f"Searching for APIs with query: {query}")
        query_embedding = self._calculate_embeddings([query])
        query_embedding = query_embedding[0]
        logger.info(f"Query embedding: {query_embedding.embedding}")

        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding.embedding,
            limit=5,
            score_threshold=0.4,
        )
        logger.info(f"Search results: {search_result}")

        return search_result
