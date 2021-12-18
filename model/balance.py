class Balance:

    __slots__ = ("asset", "balance", "free")

    def __init__(self, asset: str, balance, free):
        self.asset = asset
        self.balance = float(balance)
        self.free = float(free)

    @property
    def used(self):
        return self.balance - self.free

    def __iadd__(self, other):
        self.balance += other
        return self

    def __isub__(self, other):
        self.balance -= other
        return self

    def __gt__(self, other):
        return self.balance > other

    def __ge__(self, other):
        return self.balance >= other

    def __lt__(self, other):
        return self.balance < other

    def __le__(self, other):
        return self.balance <= other

    def __eq__(self, other):
        return self.balance == other

    def __ne__(self, other):
        return self.balance != other

    def __str__(self):
        return f"{self.asset}: {self.balance}"
