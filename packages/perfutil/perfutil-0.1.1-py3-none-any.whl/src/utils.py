
import redis
import clickhouse_driver
import logging
import json

log = logging.getLogger(__name__)


class RedisUtils:
    def __init__(self, host, port, db):
        self.redis = redis.Redis(host=host, port=port, db=db)

    def set(self, key, value):
        self.redis.set(key, value)

    def get(self, key):
        return self.redis.get(key)

    def delete(self, *keys):
        self.redis.delete(*keys)

    def publish(self, channel, message):
        self.redis.publish(channel, json.dumps(message))

    def pubsub(self):
        return self.redis.pubsub()


class ClickHouseUtils:
    def __init__(self, host, port, database, user, password):
        self.connection = clickhouse_driver.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )

    def execute_query(self, query):
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
        return result

