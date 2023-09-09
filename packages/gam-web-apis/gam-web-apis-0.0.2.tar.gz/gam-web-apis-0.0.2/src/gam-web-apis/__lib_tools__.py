
from time import time


def cache_expire(maxAge: int = 600):
    """parameter `maxAge` in seconds"""
    startTime = 0
    method = None
    cache = None

    def caller(self, *args, **kwds):
        nonlocal cache, startTime
        if time() > startTime + maxAge:
            startTime = time()
            cache = method(self, *args, **kwds)
        return cache

    def __method__(__method__):
        nonlocal method
        method = __method__
        return caller
    return __method__
