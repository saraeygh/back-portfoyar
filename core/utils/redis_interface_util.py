import json
import numpy as np
import redis
from samaneh.settings import REDIS_HOST


class Int64Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.int64):
            return int(obj)
        return super().default(obj)


class RedisInterface:
    def __init__(self, host: str = REDIS_HOST, port: int = 6379, db: int = 1):
        self.client = redis.Redis(host=host, port=port, db=db)

    def get_list_of_field_values(self, list_key: str, field_name: str) -> list:
        length = self.client.llen(list_key)
        fields_list = [
            json.loads(self.client.lindex(list_key, i))[field_name]
            for i in range(length)
        ]

        return fields_list

    def bulk_push_list_of_dicts(self, list_key: str, list_of_dicts: list):
        self.client.delete(list_key)
        serialized_data = json.dumps(list_of_dicts, cls=Int64Encoder)
        self.client.set(list_key, serialized_data)

    def get_list_of_dicts(self, list_key: str):
        retrieved_data = self.client.get(list_key)
        if retrieved_data is None:
            retrieved_data = []
        else:
            retrieved_data = json.loads(retrieved_data.decode("utf-8"))

        return retrieved_data
