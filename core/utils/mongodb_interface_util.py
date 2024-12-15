from pymongo import MongoClient
from samaneh.settings.common import MONGODB_HOST


class MongodbInterface:
    def __init__(
        self,
        db_name: str,
        collection_name: str = "not_set",
        host: str = MONGODB_HOST,
        port: int = 27017,
    ):
        self.client = MongoClient(host=host, port=port)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def insert_docs_into_collection(self, documents: list):
        self.collection.delete_many({})
        self.collection.insert_many(documents=documents)
