from typing import Literal, Any

import redis
import json

from create_bot import config, logger

r = redis.Redis(host=config.rds.host, port=config.rds.port, db=config.rds.db)


class RedisConnector:
    r = redis.Redis(host=config.rds.host, port=config.rds.port, db=config.rds.db)

    @classmethod
    def redis_start(cls):
        for db in ["users"]:
            if cls.get_redis(db) is None:
                cls.r.set(db, json.dumps(list()))
        logger.info('Redis connected OKK')

    @classmethod
    def append_redis(cls, redis_db: Literal["users"], value: Any):
        current_value = cls.get_redis(redis_db=redis_db)
        current_value.append(value)
        cls.r.set(redis_db, json.dumps(current_value))

    @classmethod
    def get_redis(cls, redis_db: Literal["users"]) -> list:
        response = cls.r.get(redis_db)
        if not response:
            return None
        response = cls.r.get(redis_db).decode('utf=8')
        result = json.loads(response)
        return result
