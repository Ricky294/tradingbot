class Balance:
    def __init__(self, asset: str, balance, free):
        self.asset = asset
        self.balance = float(balance)
        self.free = float(free)

    @property
    def used(self):
        return self.balance - self.free
