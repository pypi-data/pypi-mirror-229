import asyncio
import re
from typing import Optional, List

import aiohttp

from finclaw.config import logger
from finclaw.config import settings
from finclaw.vendor.exceptions import NotSuccessfull

API_BASE = "https://financialmodelingprep.com/api/v3/"


# 30 API/Seconds limit

async def _call_api(session, url: str, payload: str, querystring: dict, error_count=0) -> dict:
    if settings.FMP_API_KEY == "":
        raise ValueError("You need to specify FMP_API_KEY")
    querystring["apikey"] = settings.FMP_API_KEY
    async with session.get(url, data=payload, params=querystring) as resp:
        try:
            json_response = await resp.json()
        except aiohttp.ContentTypeError as e:
            logger.exception("Could not parse response")
        return json_response


async def get_symbols(session: aiohttp.ClientSession):
    querystring = {}
    return await _call_api(
        session,
        f"{API_BASE}symbol/available-tsx",
        payload="",
        querystring={},
    )


async def get_stock_candle(session: aiohttp.ClientSession, symbol: str, resolution: str):
    if resolution == "1":
        return await _call_api(
            session, f"{API_BASE}historical-chart/1min/{symbol}", payload="", querystring={}
        )
    else:
        raise NotImplementedError("Only 1 minute resolution is supported")
