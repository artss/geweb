import gevent
from redis.client import Redis
import hashlib
import json

class RedisPool(Redis):
    __instances = {}
    def __new__(cls, *args, **kwargs):
        k = str(args)+str(kwargs)
        if k not in cls.__instances:
            cls.__instances[k] = Redis.__new__(cls, *args, **kwargs)
        return cls.__instances[k]

    def __init__(self, addr, db=0):
        if not addr:
            raise ValueError('Invalid redis address')
        if addr.startswith('unix://'):
            cargs = {'unix_socket_path':addr.replace('unix://', '')}
        elif addr.startswith('tcp://'):
            h = addr.replace('tcp://', '').split(':')
            cargs = {'host': h[0]}
            if len(h) == 2:
                cargs['port'] = int(h[1])
        else:
            raise ValueError('Invalid redis address')
        Redis.__init__(self, **cargs)

