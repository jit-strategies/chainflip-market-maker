import asyncio

import chainflip_partnernet.utils.constants as CONSTANTS
import chainflip_partnernet.utils.logger as log

from chainflip_partnernet.utils.data_types import LimitOrder, RangeOrder
from chainflip_partnernet.market_maker.market_maker import MarketMaker


logger = log.setup_custom_logger('root')


class StrategyStream:
    """
    Stream strategy
    Open a limit order and range order with an updated price every 30 seconds.
    After 30 seconds burn the orders and create a new order.
    In this simulator these orders are not filled as the AMM is only a dummy.
    """
    def __init__(
            self,
            data_feeds: dict,
            active_pools: dict,
            market_maker: MarketMaker
    ):
        self._base_asset = None
        self._quote_asset = 'Usdc'
        self._data = data_feeds
        self._pools = active_pools
        self._market_maker = market_maker
        self._limit_order_buy = None
        self._limit_order_sell = None
        self._range_order = None
        self._limit_order_list = list()
        self._range_order_list = list()
        self._order_active_time = 50
        self._active_orders = list()

    def open_orders(self):
        logger.info(f'Open limit orders: {self._market_maker.open_limit_orders}')
        logger.info(f'Open range orders: {self._market_maker.open_range_orders}')

    def _create_limit_order_candidate(self, amount: float, price: float, side: CONSTANTS.Side):
        if side == CONSTANTS.Side.BUY:
            self._limit_order_buy = LimitOrder(amount, price, side, self._base_asset)
            logger.info(f"Created buy limit order candidate: {self._limit_order_buy}")
            return
        elif side == CONSTANTS.Side.SELL:
            self._limit_order_sell = LimitOrder(amount, price, side, self._base_asset)
            logger.info(f"Created sell limit order candidate: {self._limit_order_sell}")
            return
        else:
            logger.error(f'Side is incorrectly set for limit order: {side}')
            return

    def _create_range_order_candidate(
            self,
            amount: float,
            lower_price: float,
            upper_price: float,
            minimum_amount: float = None,
            order_type: CONSTANTS.RangeOrderType = CONSTANTS.RangeOrderType.LIQUIDITY
    ):
        self._range_order = RangeOrder(amount, lower_price, upper_price, self._base_asset, minimum_amount, order_type)
        logger.info(f"Created range order candidate: {self._range_order}")

    def _create_orders(self, assets: list):
        for asset in assets:
            try:
                self._data[asset].data.close
            except:
                logger.info(f'send_orders: strategy waiting on data from binance for asset: {asset}')
                return

            pool_price = self._pools[asset].pool_price
            current_price = self._data[asset].data.close

            logger.info(f'Current pool price for asset {asset}: {pool_price}, current market price: {current_price}')
            self._base_asset = asset

            self._create_limit_order_candidate(
                amount=self._market_maker.book_balance[self._base_asset] * 0.0001,
                price=current_price - (current_price * 0.0001),
                side=CONSTANTS.Side.BUY
            )
            self._limit_order_list.append(self._limit_order_buy)

            self._create_limit_order_candidate(
                amount=self._market_maker.book_balance[self._base_asset] * 0.0001,
                price=current_price + (current_price * 0.0001),
                side=CONSTANTS.Side.SELL
            )
            self._limit_order_list.append(self._limit_order_sell)

            self._create_range_order_candidate(
                amount=self._market_maker.book_balance[self._base_asset] * 0.00025,
                lower_price=pool_price - (current_price * 0.001),
                upper_price=pool_price + (current_price * 0.001),
                minimum_amount=None,
                order_type=CONSTANTS.RangeOrderType.LIQUIDITY
            )
            self._range_order_list.append(self._range_order)

    async def send_orders(self, assets: list):
        self.open_orders()
        if len(self._limit_order_list) > 0 or len(self._range_order_list) > 0:
            logger.info('send_orders: awaiting burn for open orders')
            await self.cancel_orders()

        self._create_orders(assets)
        await self._market_maker.send_limit_orders(self._limit_order_list)
        await self._market_maker.send_range_orders(self._range_order_list)

    async def cancel_orders(self):
        self.open_orders()
        await self._market_maker.burn_limit_orders(self._limit_order_list)
        await self._market_maker.burn_range_orders(self._range_order_list)

    async def sleep(self, time: int = None):
        if time is None:
            await asyncio.sleep(self._order_active_time)
        else:
            await asyncio.sleep(time)

    async def run_strategy(self, assets: list):
        logger.info(f'Initialised strategy: steaming quotes for {self._order_active_time - 12} seconds')
        logger.info(f'Strategy will sleep for 30 seconds to allow data to be pulled')
        await self.sleep(30)
        while True:
            await self._market_maker.get_asset_balances()
            await self.send_orders(assets)
            await self.sleep()
            await self._market_maker.get_asset_balances()
            await self.cancel_orders()
            await self.sleep(7)
            self._limit_order_list.clear()
            self._range_order_list.clear()
