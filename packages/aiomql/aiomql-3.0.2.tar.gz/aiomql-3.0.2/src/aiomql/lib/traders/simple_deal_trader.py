import logging
from datetime import datetime

from ...utils import dict_to_string
from ...trader import Trader
from ...core.constants import OrderType, OrderTime

from ...result import Result

logger = logging.getLogger()


class DealTrader(Trader):
    """A base class for placing trades based on the number of pips to target"""

    async def create_order(self, *, order_type: OrderType, pips: float = 0):
        """Using the number of target pips it determines the lot size, stop loss and take profit for the order,
        and updates the order object with the values.

        Args:
            order_type (OrderType): Type of order
            pips (float): Target pips
        """
        volume = await self.ram.get_volume(symbol=self.symbol, pips=pips)
        self.order.volume = volume
        self.order.type = order_type
        await self.set_order_limits(pips=pips)
