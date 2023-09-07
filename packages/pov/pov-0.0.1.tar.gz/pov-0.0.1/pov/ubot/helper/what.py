import random
import openai
from asyncio import gather

import httpx
from aiohttp import ClientSession

session = ClientSession()


# HTTPx Async Client
http = httpx.AsyncClient(
    http2=True,
    timeout=httpx.Timeout(40),
)

OPENAI_API = "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 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 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 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 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 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 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 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".split()

async def get(url: str, *args, **kwargs):
    async with session.get(url, *args, **kwargs) as resp:
        try:
            data = await resp.json()
        except Exception:
            data = await resp.text()
    return data


async def head(url: str, *args, **kwargs):
    async with session.head(url, *args, **kwargs) as resp:
        try:
            data = await resp.json()
        except Exception:
            data = await resp.text()
    return data


async def post(url: str, *args, **kwargs):
    async with session.post(url, *args, **kwargs) as resp:
        try:
            data = await resp.json()
        except Exception:
            data = await resp.text()
    return data


async def multiget(url: str, times: int, *args, **kwargs):
    return await gather(*[get(url, *args, **kwargs) for _ in range(times)])


async def multihead(url: str, times: int, *args, **kwargs):
    return await gather(*[head(url, *args, **kwargs) for _ in range(times)])


async def multipost(url: str, times: int, *args, **kwargs):
    return await gather(*[post(url, *args, **kwargs) for _ in range(times)])


async def resp_get(url: str, *args, **kwargs):
    return await session.get(url, *args, **kwargs)


async def resp_post(url: str, *args, **kwargs):
    return await session.post(url, *args, **kwargs)

