import datetime

from dataclasses import dataclass
from typing import Optional

import chainflip_perseverance.utils.constants as CONSTANTS


@dataclass
class PrewitnessedSwap:
    base_asset: str
    pair_asset: str
    amount: int
    end_time: datetime.datetime

    def __lt__(self, other):
        return self.end_time < other.end_time

    def __str__(self):
        return f'Witnessed - {self.base_asset} to {self.pair_asset}, amount={self.amount}'


@dataclass
class LimitOrder:
    amount: float
    price: float
    base_asset: str
    pair_asset: str
    id: int
    side: CONSTANTS.Side
    timestamp: Optional[datetime.datetime] = None

    def __str__(self):
        return f'Limit Order - {self.base_asset}{self.pair_asset}: ' \
               f'price = {self.price}, amount = {self.amount}, id = {self.id}, side = {self.side.name}, ' \
               f'timestamp = {self.timestamp}'


@dataclass
class RangeOrder:
    lower_price: float
    upper_price: float
    base_asset: str
    pair_asset: str
    id: int
    type: CONSTANTS.RangeOrderType
    timestamp: Optional[datetime.datetime] = None
    amount: Optional[float] = None
    min_amounts: Optional[tuple] = None
    max_amounts: Optional[tuple] = None

    def __str__(self):
        if self.type.value == CONSTANTS.RangeOrderType.LIQUIDITY.value:
            return f'Range Order - {self.base_asset}{self.pair_asset}: ' \
                   f'lower_price = {self.lower_price}, upper_price = {self.upper_price}, ' \
                   f'amount = {self.amount}, id = {self.id}, timestamp = {self.timestamp}'
        else:
            return f'Range Order - {self.base_asset}{self.pair_asset}: ' \
                   f'lower_price = {self.lower_price}, upper_price = {self.upper_price}, ' \
                   f'id = {self.id}, timestamp = {self.timestamp}, ' \
                   f'min_amounts = {self.min_amounts}, max_amounts = {self.max_amounts}'


@dataclass
class BinanceKline:
    start_time: datetime.datetime
    end_time: datetime.datetime
    ticker: str
    interval: str
    open: float = None
    close: float = None
    high: float = None
    low: float = None
    volume: float = None

    def __str__(self):
        return f'Binance Candle - start_time: {self.start_time}, end_time: {self.end_time}, ticker: {self.ticker}, ' \
               f'interval: {self.interval}, open: {self.open}, close: {self.close}, ' \
               f'high: {self.high}, low: {self.low},' \
               f'volume: {self.volume}'
