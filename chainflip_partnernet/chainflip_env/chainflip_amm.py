
import chainflip_partnernet.utils.logger as log
import chainflip_partnernet.utils.format as formatter

from chainflip_partnernet.utils.data_types import Order, Swap


logger = log.setup_custom_logger('root')


class Amm(object):
    """
    Amm simulator. No swaps are conducted but demonstrates timings and received information
    """
    def __init__(self):
        self._orders = list()
        self._swaps = list()

    def add_order(self, order: Order):
        order.asset = formatter.asset_to_str(order.asset)
        self._orders.append(order)

    def add_swaps(self, swaps: list):
        self._swaps = swaps

    def begin_matching_1(self):
        logger.info('Executing swaps')
        while len(self._orders) != 0:
            self.begin_matching()

        self._swaps.clear()
        self._orders.clear()

    def begin_matching(self):
        for order in self._orders:
            for swap in self._swaps:
                if order.asset != swap.destination_asset:
                    break

                self.match(order, swap)
                if order.amount > 0:
                    continue
                else:
                    self._orders.remove(order)
                    break

    def match(self, order: Order, swap: Swap):
        if order.amount == swap.amount:
            logger.info(
                f'Market maker {order.market_maker_id} matched all of swap. '
                f'Swapped {swap.amount} {swap.base_asset} for {swap.destination_asset} at {order.price} '
            )
            order.amount = 0
            swap.amount = 0

        elif order.amount < swap.amount:
            logger.info(
                f'Market maker {order.market_maker_id} matched some of swap. '
                f'Swapped {order.amount} {swap.base_asset} for {swap.destination_asset} at {order.price} '
            )
            order.amount = 0
            swap.amount = swap.amount - order.amount

        elif order.amount > swap.amount:
            logger.info(
                f'Market maker {order.market_maker_id} matched all of swap with spare liquidity. '
                f'Swapped {order.amount} {swap.base_asset} for {swap.destination_asset} at {order.price} '
            )
            order.amount = order.amount - swap.amount
            swap.amount = 0

        if swap.amount <= 0:
            self._swaps.remove(swap)
