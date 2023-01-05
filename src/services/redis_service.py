import pickle

import redis


class CacheClient:

    def __init__(self, config):
        pool = redis.ConnectionPool(host=config.host, port=config.port, db=config.db)
        self.redis_client = redis.Redis(connection_pool=pool)

    def set(self, key: list, value: list):
        key = pickle.dumps(key)
        value = pickle.dumps(value)
        return self.redis_client.set(key, value)


    def get(self, key: list):
        key = pickle.dumps(key)
        return pickle.loads(self.redis_client.get(key))

    def delete(self, key: list):
        key = pickle.dumps(key)
        return self.redis_client.delete(key)


    def exists(self, key: list):
        print(key)
        key = pickle.dumps(key)
        return self.redis_client.exists(key)