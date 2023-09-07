"""Risk Assessment and Management"""
from .account import Account


class RAM:
    account: Account = Account()
    risk_to_reward: float
    risk: float
    amount: float
    pips: float
    volume: float

    def __init__(self, **kwargs):
        """Risk Assessment and Management. All provided keyword arguments are set as attributes.

        Args:
            kwargs (Dict): Keyword arguments.

        Defaults:
            risk_to_reward (float): Risk to reward ratio 1
            risk (float): Percentage of account balance to risk per trade 0.01 # 1%
            amount (float): Amount to risk per trade in terms of base currency 10
            pips (float): Target pips 10
            volume (float): Volume to trade 0.05


        """
        self.risk_to_reward = kwargs.pop('risk_to_reward', 1)
        self.risk = kwargs.pop('risk', 0.01)
        self.amount = kwargs.pop('amount', 10)
        self.pips = kwargs.pop('pips', 10)
        self.volume = kwargs.pop('volume', 0.05)
        [setattr(self, key, value) for key, value in kwargs.items()]

    async def get_amount(self) -> float:
        """Calculate the amount to risk per trade.

        Returns:
            float: Amount to risk per trade
        """
        await self.account.refresh()
        return self.account.margin_free * self.risk
