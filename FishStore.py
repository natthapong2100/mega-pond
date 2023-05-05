import pickle
import time
from dataclasses import dataclass
from typing import Dict, List, Union

import redis

from Fish import Fish
from FishData import FishData
from logging_utils import get_logger
# from logging_utils import get_logger
# import loggingutils
# import logging


def current_milli_time():
    return round(time.time() * 1000)


@dataclass
class ExampleObject:
    name: str
    unit_price: float
    quantity_on_hand: int = 0


log = get_logger("redis")


def connect_to_redis(host="localhost", port=6379, password=None, retries=5, retry_interval=1, db=0) -> Union[redis.StrictRedis, None]:
    for i in range(retries):
        try:
            r = redis.StrictRedis(host=host,
                                  port=port,
                                  password=password,
                                  db=db)
            if r.ping():
                log.info(f"connected to Redis at {host}:{port}")
                return r
            else:
                raise redis.ConnectionError()

        except redis.ConnectionError:
            if i < retries - 1:
                log.warning(
                    f"failed to connect to Redis at {host}:{port}, retrying in {retry_interval} second")
                time.sleep(retry_interval)
            else:
                log.error(
                    f"failed to connect to Redis at {host}:{port}, after {retries} attempts")
                return None


class FishStore:
    def __init__(self, redis, db_i):
        self.redis: redis.StrictRedis = redis
        self.db_i = db_i

    def add_fish(self, fish: FishData):
        self.redis.set(fish.getId(), pickle.dumps(fish), ex=fish.getLifetime())

    def remove_fish(self, fish_ids: List[str]):
        self.redis.delete(*fish_ids)

    # TODO: need to compare performance later
    def remove_batch(self, fish_ids: List[str]):
        pipe = self.redis.pipeline(transaction=False)
        for key in fish_ids:
            pipe.delete(key)

    def get_fishes(self) -> Dict[str, Fish]:
        fish_ids = self.redis.keys()
        fishes_data = [
            pickle.loads(data) for data in self.redis.mget(fish_ids) if data is not None
        ]
        fishes = [Fish(fish.x, fish.y, data=fish) for fish in fishes_data]
        return dict(zip(fish_ids, fishes))

    def set_pheromone(self, pheromone: int):
        self.redis.select(self.db_i+1)
        self.redis.set("pheromone", pheromone)
        self.redis.select(self.db_i)

    def get_pheromone(self) -> int:
        self.redis.select(self.db_i+1)
        pheromone = self.redis.get("pheromone")
        self.redis.select(self.db_i)
        return int(pheromone) if pheromone is not None else 0


# TODO: get address from env

# pubsub - remove expire (dead) fish
def event_handler(msg):
    try:
        key = msg["data"].decode("utf-8")
        log.info(f"Key expire event: msg: {msg}, key: {key}")
    except Exception as e:
        log.exception(f"pubsub handler error: {e}")
