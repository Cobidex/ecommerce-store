import redis
from os import getenv

redisClient = redis.Redis(host=getenv('REDIS_HOST'),
                          port=getenv('REDIS_PORT'), decode_responses=True)
