import asyncio

import click
import pandas as pd
from pandas import Timestamp

from finclaw.config import settings
from finclaw.data_store.store import PriceStore
from finclaw.utils.cli_utils import Date
from finclaw.vendor import twelvedata as twelve
from finclaw.vendor.finnhub.pull_dividends import pull_dividend_data
from finclaw.vendor.finnhub.pull_financials import pull_financials
from finclaw.vendor.finnhub.pull_insider_information import pull_insider_information
from finclaw.vendor.finnhub.pull_ohcl import pull_ohcl_data
from finclaw.vendor.finnhub.pull_ownership import pull_ownership_data_for
from finclaw.vendor.finnhub.pull_splits import pull_splits
from finclaw.vendor.finnhub.symbols import get_symbols_for
from finclaw.vendor.fmp import fmp


@click.group
def main():
    pass


def fmp_vendor(*, store, frequency, include_information, market, start: pd.Timestamp, end: pd.Timestamp):
    if "p" in include_information:
        symbols = asyncio.run(fmp.get_symbol_table(market=market)).to_pandas().ticker.values
        fmp.pull_symbols(store=store, market=market, start=start, end=end)
        fmp.pull_ohcl_data(store=store, symbols=symbols, start=start, end=end, frequency=frequency)
    else:
        raise NotImplementedError()


def twelve_data_vendor(*, store, frequency: str, include_information: str, market_id_code: str, start: pd.Timestamp,
                       end: pd.Timestamp):
    if "p" in include_information:
        symbols = asyncio.run(twelve.get_symbol_table(market_id_code=market_id_code)).to_pandas().ticker.values
        twelve.pull_symbols(store=store, market_id_code=market_id_code, start=start, end=end)
        twelve.pull_ohcl_data(store=store, symbols=symbols, start=start, end=end, frequency=frequency,
                              market_id_code=market_id_code)
    else:
        raise NotImplementedError()


@main.command()
@click.option(
    "-s",
    "--start",
    type=Date(tz="utc", as_timestamp=False),
    help="The start date from which to pull data.",
    required=True
)
@click.option(
    "-e",
    "--end",
    type=Date(tz="utc", as_timestamp=False),
    help="The end date from which to pull data.",
    required=True
)
@click.option(
    "-f",
    "--frequency",
    type=click.Choice(["1", "5", "15", "30", "60", "D", "W", "M"]),
    help="What's the frequency the data should be.",
    required=True
)
@click.option(
    "-m",
    "--market",
    type=click.Choice(["US", "TO"]),
    help="What's the market to use?",
    required=False
)
@click.option(
    "-mic",
    "--market-id-code",
    help="Market identification code",
    required=False
)
@click.option(
    "-ic",
    "--include-information",
    help="Information to include",
    required=True
)
@click.option(
    "-v",
    "--vendor",
    type=click.Choice(["finnhub", "fmp", "twelvedata"]),
    help="Vendor to use",
    required=True
)
def grab(start: Timestamp, end: Timestamp, frequency: str, market: str, include_information: str, vendor: str,
         market_id_code: str):
    """
    Grabs data from a vendor and stores it on local
    :param start: Normalized (floor down) so 2012-01-01T12:15:16 -> 2012-01-01T00:00:00
    :param end: Same as start

    Args:
        include_company_information:
        market: Market to pull data from: US, TO ...
        frequency: Granularity of the data: 1, 5, 15, 30, 60, D, W, M
    """
    store = PriceStore(settings.TRADE_ENGINE_DATA)
    if vendor == "finnhub":
        finnhub_vendor(store, end, frequency, include_information, market, start)
    elif vendor == "fmp":
        fmp_vendor(store=store, frequency=frequency, include_information=include_information, market=market,
                   start=start, end=end)
    elif vendor == "twelvedata":
        twelve_data_vendor(store=store, frequency=frequency, include_information=include_information,
                           market_id_code=market_id_code,
                           start=start, end=end)
    return 0


def finnhub_vendor(store, end, frequency, include_information, market, start):
    _, symbols = get_symbols_for(market)

    if "o" in include_information:
        pull_ownership_data_for(store=store, symbols=symbols, start=start, end=end)
    if "i" in include_information:
        pull_insider_information(store=store, symbols=symbols, start=start, end=end)
    if "f" in include_information:
        pull_financials(store=store, symbols=symbols, start=start, end=end)
    if "d" in include_information:
        pull_dividend_data(store=store, symbols=symbols, start=start, end=end)
    if "s" in include_information:
        pull_splits(store=store, symbols=symbols, start=start, end=end)
    if "p" in include_information:
        pull_ohcl_data(store=store,
                       start=start,
                       end=end,
                       frequency=frequency,
                       market=market,
                       include_company_information=True)


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    main()

# See PyCharm help at https://wfw.jetbrains.com/hetp/pycharm/
