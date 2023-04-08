from functools import wraps
from inspect import isasyncgenfunction, iscoroutinefunction
from io import BytesIO
from typing import Callable, List, Optional, TypeVar, Union

_T = TypeVar("_T")
_RES = TypeVar("_RES", str, bytes, dict, list, tuple, BytesIO, None)

def cache(
    maxsize: int=128,
    key_func: Optional[Callable]=None,
    eviction_policy: Optional[Callable]=None,
) -> Callable[[_T], _T]:
    cache: dict[str, _RES] = {}
    order: List[str] = []

    def decorator(func: _T) -> _T:
        if iscoroutinefunction(func) or isasyncgenfunction(func):
            @wraps(func)
            async def inner(*args, no_cache=False, **kwargs) -> _RES:
                if no_cache:
                    return await func(*args, **kwargs)

                key = key_func(*args, **kwargs) if key_func else f"{args}-{kwargs}"

                if key in cache:
                    if eviction_policy:
                        eviction_policy(key)
                    return cache[key]

                try:
                    res = await func(*args, **kwargs)
                except Exception as e:
                    raise e
                else:
                    if len(cache) >= maxsize:
                        oldest_key = order.pop(0)
                        del cache[oldest_key]
                    
                    cache[key] = res
                    order.append(key)
                    return res
                
        elif not iscoroutinefunction(func) or not isasyncgenfunction(func):
            @wraps(func)
            def inner(*args, no_cache=False, **kwargs) -> _RES:
                if no_cache:
                    return func(*args, **kwargs)

                key = key_func(*args, **kwargs) if key_func else f"{args}-{kwargs}"

                if key in cache:
                    if eviction_policy:
                        eviction_policy(key)
                    return cache[key]

                try:
                    res = func(*args, **kwargs)
                except Exception as e:
                    raise e
                else:
                    if len(cache) >= maxsize:
                        oldest_key = order.pop(0)
                        del cache[oldest_key]
                    
                    cache[key] = res
                    order.append(key)
                    return res
                
        else:
            raise TypeError(f'Invalid type for function {func.__name__}')

        return inner

    return decorator