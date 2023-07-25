import datetime
from dataclasses import dataclass

import chainflip_partnernet.utils.constants as CONSTANTS


@dataclass
class Swap:
    base_asset: str
    destination_asset: str
    amount: float
    key: str

    def __str__(self):
        return f'Swap - {self.base_asset} to {self.destination_asset}, amount={self.amount}'


@dataclass
class Order:
    price: float
    amount: float
    asset: str
    market_maker_id: str

    def __str__(self):
        return f'Order - {self.asset}: price={self.price}, amount={self.amount}'


@dataclass
class LimitOrder:
    amount: float
    price: float
    side: CONSTANTS.Side
    asset: str

    def __str__(self):
        return f'Limit Order - {self.asset}: price = {self.price}, amount = {self.amount}, side = {self.side}'


@dataclass
class RangeOrder:
    amount: float
    lower_price: float
    upper_price: float
    asset: str
    minimum_amount: float = None
    type: CONSTANTS.RangeOrderType = CONSTANTS.RangeOrderType.LIQUIDITY

    def __str__(self):
        return f'Range Order - {self.asset}:, lower_price = {self.lower_price}, ' \
               f'upper_price = {self.upper_price}, amount = {self.amount}'


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
