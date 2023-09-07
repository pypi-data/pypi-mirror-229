import redis
import pickle

# A dictionary of connection pools, based on the parameters used
# when connecting. This is so we don't have an unwieldy number of
# connections
connectionPools = {}


def getRedis(**kwargs):
    """
    Match up the provided kwargs with an existing connection pool.
    In cases where you may want a lot of queues, the redis library will
    by default open at least one connection for each. This uses redis'
    connection pool mechanism to keep the number of open file descriptors
    tractable.

    Connection code Cribbed from defunct QR3 lib.
    """
    key = ":".join((repr(key) + "=>" + repr(value)) for key, value in list(kwargs.items()))
    try:
        return redis.Redis(connection_pool=connectionPools[key])
    except KeyError:
        cp = redis.ConnectionPool(**kwargs)
        connectionPools[key] = cp
        return redis.Redis(connection_pool=cp)


class Queue:
    """A simple implementation of message queuing in redis.
    We can't push python data structures directly into redis -
    must pickle to push and unpickle to retrieve.
    """

    def __init__(self, name, **kwargs):
        self.name = name
        self.redis = getRedis(**kwargs)

    def push(self, message):
        message = pickle.dumps(message)
        self.redis.lpush(self.name, message)

    def pop(self):
        raw_message = self.redis.rpop(self.name)
        if raw_message:
            message = pickle.loads(raw_message)
            return message

        return None
