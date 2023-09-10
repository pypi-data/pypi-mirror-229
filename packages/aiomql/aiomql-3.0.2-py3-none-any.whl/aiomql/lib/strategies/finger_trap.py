import asyncio
import logging
from typing import Literal
from dataclasses import dataclass
from zoneinfo import ZoneInfo
from datetime import datetime

from ..traders.simple_deal_trader import DealTrader, Trader
from ... import Symbol
from ...strategy import Strategy
from ...core.constants import TimeFrame, OrderType
from ...candle import Candle, Candles

logger = logging.getLogger(__name__)


@dataclass
class Entry:
    """
    Entry class for FingerTrap strategy.Will be used to store entry conditions and other entry related data.

    Attributes:
        bearish (bool): True if the market is bearish
        bullish (bool): True if the market is bullish
        ranging (bool): True if the market is ranging
        snooze (float): Time to wait before checking for entry conditions
        trend (str): The current trend of the market
        last_candle (Candle): The last candle of the market
        new (bool): True if the last candle is new
        order_type (OrderType): The type of order to place
        pips (int): The number of pips to place the order from the current price
    """
    bearish: bool = False
    bullish: bool = False
    ranging: bool = True
    trending: bool = False
    trend: Literal['ranging', 'bullish', 'bearish'] = 'ranging'
    snooze: float = 0
    last_trend_time: float = 0
    last_entry_time: float = 0
    new: bool = True
    order_type: OrderType | None = None
    pips: float = 10

    def update(self, **kwargs):
        fields = self.__dict__
        for key in kwargs:
            if key in fields:
                setattr(self, key, kwargs[key])
        match self.trend:
            case 'ranging':
                self.ranging = True
                self.trending = self.bullish = self.bearish = False
            case 'bullish':
                self.ranging = self.bearish = False
                self.bullish = self.trending = True
            case 'bearish':
                self.ranging = self.bullish = False
                self.bearish = self.trending = True


class FingerTrap(Strategy):
    trend_time_frame: TimeFrame
    entry_time_frame: TimeFrame
    trend: int
    fast_period: int
    slow_period: int
    entry_period: int
    parameters: dict
    prices: Candles
    name = "FingerTrap"
    pips: float
    entry_interval: float
    entry_candles_count: int
    trend_candles_count: int
    def __init__(self, *, symbol: Symbol, params: dict | None = None, trader: Trader = None):
        super().__init__(symbol=symbol, params=params)
        self.trend = self.parameters.get('trend', 3)
        self.fast_period = self.parameters.setdefault('fast_period', 8)
        self.slow_period = self.parameters.setdefault('slow_period', 34)
        self.entry_time_frame = self.parameters.setdefault('entry_time_frame', TimeFrame.M5)
        self.trend_time_frame = self.parameters.setdefault('trend_time_frame', TimeFrame.H1)
        self.trader = trader or DealTrader(symbol=self.symbol)
        self.pips = self.parameters.setdefault('pips', 10)
        self.entry: Entry = Entry(snooze=self.trend_time_frame.time, pips=self.pips)
        self.entry_period = self.parameters.setdefault('entry_period', 8)
        self.interval = self.parameters.setdefault('interval', 60)

        self.trend_candles_count = self.parameters.setdefault('trend_candles_count',
                                                              86400 // self.trend_time_frame.time)
        self.trend_candles_count = max(self.trend_candles_count, self.slow_period)
        self.entry_candles_count = self.trend_candles_count * (self.trend_time_frame.time // self.entry_time_frame.time)
        self.entry_candles_count = max(self.entry_candles_count, self.entry_period)
        self.tz = ZoneInfo('UTC')

    async def check_trend(self):
        try:
            candles = await self.symbol.copy_rates_from(timeframe=self.trend_time_frame,
                                                        date_from=datetime.now(tz=self.tz), count=self.trend_candles_count)
            current = candles[-1]
            if current.time > self.entry.last_trend_time:
                self.entry.update(new=True, last_trend_time=current.time)
            else:
                self.entry.update(new=False)
                return
            candles.ta.ema(length=self.slow_period, append=True, fillna=0)
            candles.ta.ema(length=self.fast_period, append=True, fillna=0)
            cols = {f'EMA_{self.fast_period}': 'fast', f'EMA_{self.slow_period}': 'slow'}
            candles.rename(inplace=True, **cols)
            # Compute 
            fas = candles.ta_lib.above(candles.fast, candles.slow)
            fbs = candles.ta_lib.below(candles.fast, candles.slow)
            paf = candles.ta_lib.above(candles.close, candles.fast)
            pbf = candles.ta_lib.below(candles.close, candles.slow)
            
            candles.data[fas.name] = fas
            candles.data[fbs.name] = fbs
            candles.data[paf.name] = paf
            candles.data[pbf.name] = pbf
            trend = candles[-self.trend: -1]

            if all(c for c in trend.fast_A_slow) and all(c for c in trend.close_A_fast):
                self.entry.update(trend='bullish')

            elif all(c for c in trend.fast_B_slow) and all(c for c in trend.close_B_slow):
                self.entry.update(trend='bearish')

            else:
                self.entry.update(trend='ranging', snooze=self.trend_time_frame.time)
        except Exception as exe:
            logger.error(f'{exe}. Error in {self.__class__.__name__}.check_trend')

    async def confirm_trend(self):
        try:
            candles = await self.symbol.copy_rates_from(timeframe=self.entry_time_frame, date_from=datetime.now(tz=self.tz),
                                                        count=self.entry_candles_count)
            if candles[-1].time <= self.entry.last_trend_time:
                self.entry.update(trending=False)
                return

            candles.ta.ema(length=self.entry_period, append=True, fillna=0)
            candles.rename(**{f'EMA_{self.entry_period}': 'ema'})
            cxae = candles.ta_lib.cross(candles.close, candles.ema)
            cxbe = candles.ta_lib.cross(candles.close, candles.ema, above=False)
            candles[cxae.name] = cxae
            candles[cxbe.name] = cxbe
            if self.entry.bullish and candles[-1].close_XA_ema:
                self.entry.update(snooze=self.entry_time_frame.time, order_type=OrderType.BUY)
            elif self.entry.bearish and candles[-1].close_XB_ema:
                self.entry.update(snooze=self.entry_time_frame.time, order_type=OrderType.SELL)
            else:
                self.entry.update(snooze=self.interval, order_type=None)
        except Exception as exe:
            logger.error(f'{exe} Error in {self.__class__.__name__}.confirm_trend')

    async def watch_market(self):
        if not self.entry.trending:
            await self.check_trend()
        if self.entry.trending:
            await self.confirm_trend()

    async def trade(self):
        print(f'Trading {self.symbol}')
        while True:
            try:
                await self.watch_market()
                if not self.entry.new:
                    await asyncio.sleep(0.1)
                    continue

                if self.entry.order_type is None:
                    await self.sleep(self.entry.snooze)
                    continue

                await self.trader.place_trade(order_type=self.entry.order_type, pips=self.entry.pips,
                                              params=self.parameters)
                await self.sleep(self.entry.snooze)
            except Exception as err:
                logger.error(f"Error: {err}\t Symbol: {self.symbol} in {self.__class__.__name__}.trade")
                await self.sleep(self.trend_time_frame.time)
                continue
