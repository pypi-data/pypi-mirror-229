# __init__.py

import os
import logging
from utils import RedisUtils

logger = logging.getLogger(__name__)

REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')
REDIS_DB = os.environ.get('REDIS_DB')

r = RedisUtils(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB
)

class PerfBuilder:
    def __init__(self, namespace, subtag, **extra):
        self.namespace = namespace
        self.subtag = subtag
        self.extra = extra
        self.count_value = 0

    def count(self, value):
        self.count_value = value
        return self

    def logstash(self):
        # 构建消息对象
        message = {
            'namespace': self.namespace,
            'subtag': self.subtag,
            'extra': self.extra,
            'count': self.count_value
        }
        # 将消息以JSON格式发布到Redis频道
        r.publish('test_channel', message)
        print("PUSH Metric: {}".format(message))


class PerfUtil:
    @staticmethod
    def perf(namespace="", subtag="", **extra):
        return PerfBuilder(namespace, subtag, **extra)
    

if __name__ == '__main__':
    Perf = PerfUtil()
    Perf.perf(namespace="ns", subtag="tag", extra1="1", extra2="2", extra3= "3").count(5).logstash()