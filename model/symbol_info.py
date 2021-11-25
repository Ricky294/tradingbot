from typing import List, Dict

# Example:
# {
# 'symbol': 'BTCUSDT', 'pair': 'BTCUSDT', 'contractType': 'PERPETUAL', 'deliveryDate': 4133404800000,
# 'onboardDate': 1569398400000, 'status': 'TRADING', 'maintMarginPercent': '2.5000', 'requiredMarginPercent': '5.0000',
# 'baseAsset': 'BTC', 'quoteAsset': 'USDT', 'marginAsset': 'USDT', 'pricePrecision': 2, 'quantityPrecision': 3,
# 'baseAssetPrecision': 8, 'quotePrecision': 8, 'underlyingType': 'COIN', 'underlyingSubType': [], 'settlePlan': 0,
# 'triggerProtect': '0.0500', 'liquidationFee': '0.030000', 'marketTakeBound': '0.05',
# 'filters': [
#     {'minPrice': '556.72', 'maxPrice': '4529764', 'filterType': 'PRICE_FILTER', 'tickSize': '0.01'},
#     {'stepSize': '0.001', 'filterType': 'LOT_SIZE', 'maxQty': '1000', 'minQty': '0.001'},
#     {'stepSize': '0.001', 'filterType': 'MARKET_LOT_SIZE', 'maxQty': '300', 'minQty': '0.001'},
#     {'limit': 200, 'filterType': 'MAX_NUM_ORDERS'},
#     {'limit': 10, 'filterType': 'MAX_NUM_ALGO_ORDERS'},
#     {'notional': '5', 'filterType': 'MIN_NOTIONAL'},
#     {'multiplierDown': '0.9500', 'multiplierUp': '1.0500', 'multiplierDecimal': '4', 'filterType': 'PERCENT_PRICE'}
# ],
# 'orderTypes': ['LIMIT', 'MARKET', 'STOP', 'STOP_MARKET', 'TAKE_PROFIT', 'TAKE_PROFIT_MARKET', 'TRAILING_STOP_MARKET'],
# 'timeInForce': ['GTC', 'IOC', 'FOK', 'GTX']
# }


class SymbolInfo:
    def __init__(self, **kwargs):
        self.symbol: str = kwargs["symbol"]
        self.base_asset: str = kwargs["baseAsset"]
        self.quote_asset: str = kwargs["quoteAsset"]
        self.margin_asset: str = kwargs["marginAsset"]
        self.price_precision: int = kwargs["pricePrecision"]
        self.quantity_precision: int = kwargs["quantityPrecision"]
        self.base_asset_precision: int = kwargs["baseAssetPrecision"]
        self.quote_precision: int = kwargs["quotePrecision"]
        self.underlying_type: str = kwargs["underlyingType"]
        self.filters: List[Dict] = kwargs["filters"]
        self.order_types: List[str] = kwargs["orderTypes"]
        self.time_in_force: List[str] = kwargs["timeInForce"]

    def get_filter(self, filter_type: str):
        for filter_ in self.filters:
            if filter_type == filter_["filterType"]:
                return filter_
