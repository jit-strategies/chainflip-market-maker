import asyncio

import chainflip_perseverance.utils.constants as CONSTANTS
import chainflip_perseverance.utils.logger as log

from chainflip_perseverance.utils.data_types import LimitOrder, RangeOrder
from chainflip_perseverance.market_maker.market_maker import OMS
from chainflip_perseverance.market_maker.perseverance_pools import PerseverancePools


logger = log.setup_custom_logger('root')


class StrategyStream:
    """
    Stream strategy for Eth and Btc swapping pools.
    Open a buy and sell limit order and range order for given assets.
    After 30 seconds, delete the orders and create a new order with an updated price.
    """
    def __init__(
            self,
            data_feed: dict,
            oms: OMS,
            perseverance_pools: PerseverancePools,
            active_order_time: int = 30
    ):
        self._base_asset = None
        self._pair_asset = 'Usdc'
        self._data = data_feed
        self._oms = oms
        self._pools = perseverance_pools
        self._order_time = active_order_time
        self._order_id = 0
        self._target_spread = 0.01
        self._limit_order_candidates = list()
        self._range_order_candidates = list()

    def _create_limit_order_candidate(self,
                                      amount: float,
                                      price: float,
                                      side: CONSTANTS.Side) -> LimitOrder:
        """
        create a limit order candidate
        :param amount: float amount of sold asset to supply
        :param price: float price of sold asset in terms of buy asset
        :param side: buy or sell
        :return: LimitOrder type
        """
        self._order_id += 1
        limit_order = LimitOrder(
            amount,
            price,
            base_asset=self._base_asset,
            pair_asset=self._pair_asset,
            id=self._order_id,
            side=side
        )
        logger.info(f'Created buy limit order candidate: {limit_order}')
        return limit_order

    def _create_range_order_candidate(self,
                                      amount: float,
                                      lower_price: float,
                                      upper_price: float) -> RangeOrder:
        """
        create a range order candidate
        :param amount: float amount representing the liquidity to supply
        :param lower_price: float price for the lower range
        :param upper_price: float price for the upper range
        :return: RangeOrder type
        """
        self._order_id += 1
        range_order = RangeOrder(
            lower_price,
            upper_price,
            base_asset=self._base_asset,
            pair_asset=self._pair_asset,
            id=self._order_id,
            amount=amount,
            type=CONSTANTS.RangeOrderType.LIQUIDITY
        )
        logger.info(f'Created buy limit order candidate: {range_order}')
        return range_order

    def _create_orders(self, assets: list):
        """
        create orders for assets iteratively
        :param assets: list of assets to create orders for
        """
        for asset in assets:
            try:
                asset_price = self._data[asset].data.close
            except:
                logger.info(f'_create_orders: strategy waiting on data from binance for asset: {asset}')
                return

            self._base_asset = asset
            pool_price = self._pools.pools[f'{self._base_asset}-{self._pair_asset}'].price

            logger.info(f'Current pool price for asset {asset}: {pool_price}, current market price: {asset_price}')

            limit_order_buy = self._create_limit_order_candidate(
                amount=self._oms.book_balance[self._base_asset] * 0.001,
                price=asset_price - asset_price * self._target_spread,
                side=CONSTANTS.Side.BUY
            )
            limit_order_sell = self._create_limit_order_candidate(
                amount=self._oms.book_balance[self._pair_asset] * 0.001,
                price=asset_price + asset_price * self._target_spread,
                side=CONSTANTS.Side.SELL
            )
            self._limit_order_candidates.append(limit_order_buy)
            self._limit_order_candidates.append(limit_order_sell)

            range_order = self._create_range_order_candidate(
                amount=self._oms.book_balance[self._base_asset] * 0.0025,
                lower_price=pool_price - asset_price * self._target_spread,
                upper_price=pool_price + asset_price * self._target_spread,
            )
            self._range_order_candidates.append(range_order)

    def open_orders(self):
        """
        log open orders
        """
        logger.info(f'Open limit orders: {self._oms.open_limit_orders}')
        logger.info(f'Open range orders: {self._oms.open_range_orders}')

    async def cancel_orders(self):
        """
        cancel open orders
        """
        self.open_orders()
        await self._oms.cancel_limit_orders(self._limit_order_candidates)
        await self._oms.cancel_range_orders(self._range_order_candidates)

    async def send_orders(self, assets: list):
        """
        send orders to Perseverance
        :param assets: list of assets to market make for
        """
        self.open_orders()
        if len(self._limit_order_candidates) > 0 or len(self._range_order_candidates) > 0:
            logger.info(f'send_orders: awaiting cancellation of open orders')
            await self.cancel_orders()

        self._create_orders(assets)
        await self._oms.send_limit_orders(self._limit_order_candidates)
        await self._oms.send_range_orders(self._range_order_candidates)

    async def update_pools(self):
        """
        update all pools
        """
        await self._pools.update_all_pools()

    async def update_pool_fees(self):
        """
        update pool fees
        """
        await self._pools.update_pool_fees()

    async def start_pools_websocket(self):
        """
        start pool websocket for price updates
        """
        await self._pools.start_pool_stream()

    async def sleep(self, time: int = None):
        if time is None:
            await asyncio.sleep(self._order_time - 2)
        else:
            await asyncio.sleep(time)

    async def run_strategy(self, assets: list):
        logger.info(f'Initialised strategy: steaming quotes for {self._order_time} seconds')
        logger.info(f'Strategy will sleep for 30 seconds to allow data to be pulled')
        await self.update_pool_fees()
        await self.start_pools_websocket()
        await self.sleep(30)
        while True:
            await self._oms.get_asset_balances()
            await self.update_pools()
            await self.send_orders(assets)
            await self.sleep()
            await self.cancel_orders()
            await self.sleep(6)
            self._limit_order_candidates.clear()
            self._range_order_candidates.clear()
