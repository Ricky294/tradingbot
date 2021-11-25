class Position:
    def __init__(self, **kwargs):
        self.symbol = kwargs["symbol"]
        self.initial_margin = float(kwargs["initialMargin"])
        self.maintenance_margin = float(kwargs["maintMargin"])
        self.unrealized_profit = float(kwargs["unrealizedProfit"])
        self.position_initial_margin = float(kwargs["positionInitialMargin"])
        self.open_order_initial_margin = float(kwargs["openOrderInitialMargin"])
        self.leverage = int(kwargs["leverage"])
        self.isolated = kwargs["isolated"]
        self.entry_price = float(kwargs["entryPrice"])
        self.max_notional = float(kwargs["maxNotional"])
        self.position_side = kwargs["positionSide"]
        self.position_amount = float(kwargs["positionAmt"])
        self.notional = float(kwargs["notional"])
        self.isolated_wallet = float(kwargs["isolatedWallet"])
        self.update_time = int(kwargs["updateTime"] / 1000)
