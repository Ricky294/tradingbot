from binance.client import Client

from model import SymbolInfo


def get_symbol_info(client: Client, symbol: str):
    exchange_info: dict = client.futures_exchange_info()

    symbol = symbol.upper()
    for symbol_info in exchange_info["symbols"]:
        if symbol_info["symbol"] == symbol:
            return SymbolInfo(**symbol_info)

    raise ValueError(f"Invalid symbol: {symbol}")
