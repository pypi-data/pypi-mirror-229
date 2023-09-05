"""Trader class module. Handles the creation of an order and the placing of trades"""

from datetime import datetime
from typing import TypeVar
from logging import getLogger
from .order import Order
from .symbol import Symbol as _Symbol
from .ram import RAM
from .core.models import OrderType
from .core.config import Config
from .utils import dict_to_string
from .result import Result

logger = getLogger(__name__)
Symbol = TypeVar('Symbol', bound=_Symbol)


class Trader:
    """Base class for creating a Trader object. Handles the creation of an order and the placing of trades

    Attributes:
        symbol (Symbol): Financial instrument class Symbol class or any subclass of it.
        ram (RAM): RAM instance
        order (Order): Trade order

    Class Attributes:
        name (str): A name for the strategy.
        account (Account): Account instance.
        mt5 (MetaTrader): MetaTrader instance.
        config (Config): Config instance.
    """
    config = Config()
    def __init__(self, *, symbol: Symbol, ram: RAM = None):
        """Initializes the order object and RAM instance

        Args:
            symbol (Symbol): Financial instrument
            ram (RAM): Risk Assessment and Management instance
        """
        self.symbol = symbol
        self.order = Order(symbol=symbol.name)
        self.ram = ram or RAM()

    async def create_order(self, order_type: OrderType, pips: float):
        """Using the number of target pips it determines the lot size, stop loss and take profit for the order,
        and updates the order object with the values.

        Args:
            order_type (OrderType): Type of order
            pips (float): Target pips
        """
        self.order.volume = self.ram.volume
        self.order.type = order_type
        await self.set_order_limits(pips=self.ram.pips)

    async def set_order_limits(self, pips: float):
        """Sets the stop loss and take profit for the order.

        Args:
            pips: Target pips
        """
        pips = pips * self.symbol.pip
        sl, tp = pips, pips * self.ram.risk_to_reward
        tick = await self.symbol.info_tick()
        if self.order.type == OrderType.BUY:
            self.order.sl, self.order.tp = tick.ask - sl, tick.ask + tp
            self.order.price = tick.ask
        else:
            self.order.sl, self.order.tp = tick.bid + sl, tick.bid - tp
            self.order.price = tick.bid

    async def place_trade(self, order_type: OrderType, pips: float, params: dict = None):
        """Places a trade based on the number of points to target. The order is created, checked and sent.
        """
        try:
            await self.create_order(order_type=order_type, pips=pips)
            check = await self.order.check()
            if check.retcode != 0:
                logger.warning(
                    f"Symbol: {self.order.symbol}\nResult:\n{dict_to_string(check.get_dict(include={'comment', 'retcode'}), multi=True)}")
                return

            result = await self.order.send()
            if result.retcode != 10009:
                logger.warning(
                    f"Symbol: {self.order.symbol}\nResult:\n{dict_to_string(result.get_dict(include={'comment', 'retcode'}), multi=True)}")
                return
            params = params or {}
            params['date'] = (date := datetime.utcnow())
            params['time'] = date.timestamp()
            logger.info(f"Symbol: {self.order.symbol}\nOrder: {dict_to_string(result.dict, multi=True)}\n")
            if self.config.record_trades:
                await Result(result=result, parameters=params).save_csv()
        except Exception as err:
            logger.error(f"{err}. Symbol: {self.order.symbol}\n {self.__class__.__name__}.place_trade")
