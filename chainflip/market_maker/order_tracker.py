import chainflip.utils.format as formatter

from chainflip.utils.data_types import LimitOrder, RangeOrder


class OrderTracker(object):
    """
    Simple order book tracker.
    """
    def __init__(self):
        self._limit_orders = dict()
        self._range_orders = dict()
        self._balances = dict()

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
        Adds limit order by order id to the limit_order dict
        :param order: LimitOrder type
        :return:
        """
        self._limit_orders[order.id] = order

    def add_range_order(self, order: RangeOrder):
        """
        Adds range order by order id to the range_order dict
        :param order: RangeOrder type
        :return:
        """
        self._range_orders[order.id] = order

    def update_balance(self, balances: dict):
        """
        Updates set balances from limit and range order
        :param balances: dict of open balances from the Chainflip internal balances
        :return:
        """
        for chain in balances['result'].values():
            for asset in chain:
                self._balances[asset['asset']] = formatter.hex_amount_to_decimal(asset['balance'], asset['asset'])

    def subtract_balance(self, asset: str, balance: float):
        """
        Remove amount from current balance
        :param asset: [Eth, Dot, Btc, Flip, Usdc]
        :param balance: amount to be subtracted
        :return:
        """
        self._balances[asset] -= balance

    def get_limit_order_by_key(self, order_id: int) -> LimitOrder:
        """
        Return limit order from limit_order dict by key.
        :param order_id: string object
        :return: LimitOrder type
        """
        return self._limit_orders[order_id]

    def get_range_order_by_key(self, order_id: int) -> RangeOrder:
        """
        Return range order from range_order dict by key
        :param order_id: string object
        :return: RangeOrder type
        """
        return self._range_orders[order_id]

    def remove_limit_order_by_key(self, order_id: int):
        """
        Removes limit order from the limit_order dict by order id
        :param order_id: string object
        """
        del self._limit_orders[order_id]

    def remove_range_order_by_key(self, order_id: int):
        """
        Removes range order from the range_order dict by order id
        :param order_id: string object
        """
        del self._range_orders[order_id]
