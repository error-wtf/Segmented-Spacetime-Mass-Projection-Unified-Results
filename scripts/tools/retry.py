from __future__ import annotations
import time, functools, random

def retry(max_tries=5, base_delay=1.0, jitter=0.5, exceptions=(Exception,)):
    def deco(fn):
        @functools.wraps(fn)
        def wrapped(*a, **k):
            tries, delay = 0, base_delay
            while True:
                try:
                    return fn(*a, **k)
                except exceptions as e:
                    tries += 1
                    if tries >= max_tries:
                        raise
                    time.sleep(delay + random.random()*jitter)
                    delay *= 2.0
        return wrapped
    return deco
