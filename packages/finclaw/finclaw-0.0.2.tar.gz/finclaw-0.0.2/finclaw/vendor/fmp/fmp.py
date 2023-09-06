import asyncio
from typing import Tuple, Any, List, Optional

import aiohttp
import pandas as pd
import pytz
from pandas import DataFrame, Timestamp
from tqdm import tqdm

from finclaw.data_store.schema import OHCL, STOCK_SYMBOL
from finclaw.data_store.store import PriceStore
from finclaw.vendor.fmp import fmp_client
import pyarrow as pa


async def get_symbols(session: aiohttp.ClientSession, market: str) -> pd.DataFrame:
    if market != "TO":
        raise ValueError(f"Market {market} not supported")

    symbols = await fmp_client.get_symbols(session=session)
    df = pd.DataFrame(data=symbols)
    df["mic"] = ""
    df.loc[df["stockExchange"] == "Toronto Stock Exchange", "mic"] = "XTSE"
    df.loc[df["stockExchange"] == "TSXV", "mic"] = "XTSX"
    df = df.rename(columns={"symbol": "ticker", "name": "description", "currency": "currency_name"})
    df["type"] = ""
    df["figi"] = ""
    return df[STOCK_SYMBOL.names]


async def get_ohcl_for_symbol(session: aiohttp.ClientSession, symbol: str, resolution: str) -> Optional[pd.DataFrame]:
    ohcl_json = await fmp_client.get_stock_candle(session=session, symbol=symbol, resolution=resolution)
    if not ohcl_json:
        return None
    df = pd.DataFrame(data=ohcl_json)
    df["timestamp"] = pd.to_datetime(df["date"]).dt.tz_localize('America/New_york')
    df["timestamp"] = df["timestamp"].dt.tz_convert("UTC")
    df["symbol"] = symbol
    return df[OHCL.names]


async def get_ohcl_data(session: aiohttp.ClientSession,
                        start: Timestamp,
                        end: Timestamp,
                        symbols: List[str],
                        frequency: str) -> pd.DataFrame:
    if start > end:
        raise ValueError("Start date cannot be greater than end date")
    if start.tz != pytz.UTC or end.tz != pytz.UTC:
        raise ValueError("Start and end dates must be UTC")

    print("Getting OHCL data")
    dfs = []
    for symbol in tqdm(symbols):
        symbol_df = await get_ohcl_for_symbol(session=session, symbol=symbol, resolution=frequency)
        if symbol_df is not None:
            dfs.append(symbol_df)

    result_df = pd.concat(dfs)
    return result_df[(result_df.timestamp >= start) & (result_df.timestamp <= end)]


async def get_symbol_table(market: str) -> pa.Table:
    async with aiohttp.ClientSession() as session:
        symbol_df = await get_symbols(session=session, market=market)
        return pa.Table.from_pandas(symbol_df, schema=STOCK_SYMBOL)


async def get_ohcl_table_for(start: Timestamp, end: Timestamp, symbols: List[str], frequency: str) -> pa.Table:
    async with aiohttp.ClientSession() as session:
        ohcl_df = await get_ohcl_data(session=session, start=start, end=end, symbols=symbols, frequency=frequency)
        return pa.Table.from_pandas(ohcl_df, schema=OHCL)


def pull_symbols(*, store: PriceStore, market: str, start: pd.Timestamp, end: pd.Timestamp):
    symbol_table = asyncio.run(get_symbol_table(market=market))
    store.store_symbols(symbol_table=symbol_table, start=start, end=end, vendor="fmp")


def pull_ohcl_data(*, store: PriceStore, symbols: List[str], start: Timestamp, end: Timestamp, frequency: str):
    table = asyncio.run(get_ohcl_table_for(start, end, symbols, frequency))
    store.store_prices(price_table=table, start=start, end=end, vendor="fmp", frequency=frequency)
