from asyncio import AbstractEventLoop
from io import BytesIO
from typing import TypeVar

from aiohttp import ClientSession

from .CACHE import cache
from .LOOP import AsyncManager

_RES = TypeVar("_RES", str, bytes, dict, list, tuple, BytesIO, None)


class HTTPSession(ClientSession):
    """ Abstract class for aiohttp. """
    
    def __init__(self, loop: AbstractEventLoop = None) -> None:
        super().__init__(loop=loop or AsyncManager().loop)
    
    def __del__(self):
        self.close()

@cache(maxsize=50)
async def query(url: str, method: str = "get", res_method: str = "text", *args, **kwargs) -> _RES:
    async with HTTPSession() as session:
        try:
            async with getattr(session, method.lower())(url, *args, **kwargs) as res:
                return await getattr(res, res_method)()
        except Exception as e:
            raise e

async def get(url: str, res_method: str = 'json', *args, **kwargs) -> _RES:
    async with HTTPSession() as session:
        return await query(url, "get", res_method=res_method, *args, **kwargs)

async def post(url: str, res_method: str = 'json', *args, **kwargs) -> _RES:
    async with HTTPSession() as session:
        return await query(url, "post", res_method=res_method, *args, **kwargs)

async def delete(url: str, res_method: str = 'json', *args, **kwargs) -> _RES:
    async with HTTPSession() as session:
        return await query(url, "delete", res_method=res_method, *args, **kwargs)

async def patch(url: str, res_method: str = 'json', *args, **kwargs) -> _RES:
    async with HTTPSession() as session:
        return await query(url, "patch", res_method=res_method, *args, **kwargs)

async def put(url: str, res_method: str = 'json', *args, **kwargs) -> _RES:
    async with HTTPSession() as session:
        return await query(url, "put", res_method=res_method, *args, **kwargs)
