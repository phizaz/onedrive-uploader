import time
import functools


def measure_time(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.time()
        res = fn(*args, **kwargs)
        end = time.time()
        return (res, end - start)

    return wrapper

def unit(x):
    return (x, 0.0)

def bind(x, measured_fn):
    res, time = x
    n_res, n_time = measured_fn(res)
    return (n_res, time + n_time)
