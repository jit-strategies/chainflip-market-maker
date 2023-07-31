from datetime import datetime

import chainflip_partnernet.utils.constants as CONSTANTS

from chainflip_partnernet.utils.data_types import LimitOrder, RangeOrder


class Book(object):
    """
    Simple limit order book.
    """
    def __init__(self):
        self._limit_orders = dict()
        self._range_orders = dict()
        self._balances = dict()
        self._last_limit_order_time_stamp_sell = None
        self._last_limit_order_time_stamp_buy = None
        self._last_range_order_time_stamp = None

    @property
    def limit_orders(self) -> dict:
        return self._limit_orders

    @property
    def range_orders(self) -> dict:
        return self._range_orders

    @property
    def balance(self) -> dict:
        return self._balances

    def add_limit_order(self, order: LimitOrder):
        """
        Adds limit order by current timestamp to the limit_order dict
        :param order: LimitOrder type
        :return:
        """
        timestamp = datetime.timestamp(datetime.now())
        self._limit_orders.update([(timestamp, order)])
        if order.side == CONSTANTS.Side.BUY:
            self._last_limit_order_time_stamp_buy = timestamp
        elif order.side == CONSTANTS.Side.SELL:
            self._last_limit_order_time_stamp_sell = timestamp
        else:
            raise f'Incorrect order side used for limit order: {order}'

    def add_range_order(self, order: RangeOrder):
        """
        Adds range order by current timestamp to the range_order dict
        :param order: RangeOrder type
        :return:
        """
        timestamp = datetime.timestamp(datetime.now())
        self._range_orders.update([(timestamp, order)])
        self._last_range_order_time_stamp = timestamp

    def update_balance(self, balances: dict):
        """
        Updates set balances from limit and range order
        :param balances: dict of open balances from the Chainflip internal balances
        :return:
        """
        self._balances = dict((key, value / CONSTANTS.UNIT_CONVERTER[key]) for key, value in balances.items())

    def sub_balance(self, asset: str, balance: float):
        """
        Remove amount from current balance
        :param asset: [Eth, Dot, Btc, Flip, Usdc]
        :param balance: amount to be subtracted
        :return:
        """
        self._balances[asset] -= balance

    def get_limit_order_by_timestamp(self, timestamp: datetime = None, order_side: CONSTANTS.Side = None):
        """
        Return limit order from limit_order dict by timestamp key.
        If no timestamp is given return the latest order
        :param timestamp: Datetime object
        :param order_side: Buy or Sell
        :return: LimitOrder type
        """
        if timestamp is None:
            if order_side == CONSTANTS.Side.BUY:
                timestamp = self._last_limit_order_time_stamp_buy
            elif order_side == CONSTANTS.Side.SELL:
                timestamp = self._last_limit_order_time_stamp_sell
        return self._limit_orders[timestamp]

    def get_range_order_by_timestamp(self, timestamp: datetime = None):
        """
        Return range order from range_order dict by timestamp key
        If no timestamp is given return the range order
        :param timestamp: Datetime object
        :return: RangeOrder type
        """
        if timestamp is None:
            timestamp = self._last_range_order_time_stamp
        return self._range_orders[timestamp]

    def remove_limit_order_by_timestamp(self, timestamp: datetime = None, order_side: CONSTANTS.Side = None):
        """
        Removes limit order from the limit_order dict by timestamp key
        If no timestamp is given, delete latest limit order
        :param timestamp: Datetime object
        :param order_side: Buy or Sell
        """
        if timestamp is None:
            if order_side == CONSTANTS.Side.BUY:
                timestamp = self._last_limit_order_time_stamp_buy
            elif order_side == CONSTANTS.Side.SELL:
                timestamp = self._last_limit_order_time_stamp_sell
        del self._limit_orders[timestamp]

    def remove_range_order_by_timestamp(self, timestamp: datetime = None):
        """
        Removes range order from the range_order dict by timestamp key
        If no timestamp is given, delete latest range order
        :param timestamp: Datetime object
        """
        if timestamp is None:
            timestamp = self._last_range_order_time_stamp
        del self._range_orders[timestamp]
