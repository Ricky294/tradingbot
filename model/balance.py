class Balance:

    __slots__ = ("asset", "total", "available")

    def __init__(self, asset: str, total, available):
        self.asset = asset
        self.total = float(total)
        self.available = float(available)

    @property
    def used(self):
        return self.total - self.available

    def __str__(self):
        return f"{self.asset}: {self.total}"
