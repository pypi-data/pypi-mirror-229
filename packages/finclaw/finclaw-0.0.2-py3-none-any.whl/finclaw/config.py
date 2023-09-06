import logging
import os

from pydantic import BaseSettings
from dotenv import load_dotenv


def is_running_in_jupyter():
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True  # Jupyter Notebook
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type, assume not a Jupyter Notebook
    except NameError:
        return False  # Probably standard Python interpreter


class Settings(BaseSettings):
    TRADE_ENGINE_DATA: str
    FINNHUB_API: str = ""
    FINNHUB_STORAGE: str = "./finnhub_storage/daily"

    # FMP creds
    FMP_API_KEY: str = ""

    # TwelveData creds
    TWELVEDATA_API_KEY: str = ""

    # Kraken creds
    KRAKEN_API_KEY: str
    KRAKEN_API_SECRET: str


if is_running_in_jupyter():
    load_dotenv()
    settings = Settings()
else:
    load_dotenv()
    settings = Settings()

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)
