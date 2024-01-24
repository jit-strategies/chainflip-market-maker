import asyncio

import chainflip.utils.constants as CONSTANTS
import chainflip.utils.logger as log

from chainflip.exchange.stream import ChainflipUpdates
from chainflip.utils.data_types import LimitOrder, RangeOrder
from chainflip.market_maker.order_management import OMS
from chainflip.market_maker.order_book import OrderBook
from chainflip.market_maker.pool_handler import ChainflipPools


logger = log.setup_custom_logger('root')


class StrategyStream:
    """
    Stream strategy for Eth and Btc swapping pools.
    Open a buy and sell limit order and range order for given assets.
    After 30 seconds, delete the orders and create a new order with an updated price.
    """
    def __init__(
            self,
            lp_account: str,
            base_asset: str,
            data_feed: dict,
            oms: OMS,
            perseverance_pools: ChainflipPools,
            active_order_time: int = 30
    ):
        self._lp_account = lp_account
        self._base_asset = base_asset
        self._quote_asset = 'USDC'
        self._data = data_feed
        self._oms = oms
        self._pools = perseverance_pools
        self._order_time = active_order_time
        self._order_book = OrderBook(base_asset, lp_account)
        self._chainflip_updates_stream = ChainflipUpdates(lp_account)
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
            quote_asset=self._quote_asset,
            id=hex(self._order_id),
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
            quote_asset=self._quote_asset,
            id=hex(self._order_id),
            amount=amount,
            type=CONSTANTS.RangeOrderType.LIQUIDITY
        )
        logger.info(f'Created buy limit order candidate: {range_order}')
        return range_order

    def _create_orders(self):
        """
        create orders using either:
        asset_price from Binance candle
        pool_price from Chainflip Pool
        top_bid from the top_bid on the Chainflip Pool
        top_ask from the top_ask on the Chainflip Pool
        """
        try:
            binance_price = self._data[self._base_asset].data.close
        except:
            logger.info(f'_create_orders: strategy waiting on data from binance for asset: {self._base_asset}')
            return

        pool_price = self._pools.pools[f'{self._base_asset}-{self._quote_asset}'].price
        top_bid = self._order_book.top_bid
        top_ask = self._order_book.top_ask

        logger.info(f'Current pool price for asset {self._base_asset}: {pool_price}, current market price: {binance_price}')
        logger.info(f'Best current bid: {top_bid}. Best current ask: {top_ask}')

        limit_order_buy = self._create_limit_order_candidate(
            amount=self._oms.book_balance[self._base_asset] * 0.001,
            price=binance_price - 1 * self._target_spread,
            side=CONSTANTS.Side.BUY
        )
        limit_order_sell = self._create_limit_order_candidate(
            amount=self._oms.book_balance[self._base_asset] * 0.001,
            price=binance_price + 1 * self._target_spread,
            side=CONSTANTS.Side.SELL
        )
        self._limit_order_candidates.append(limit_order_buy)
        self._limit_order_candidates.append(limit_order_sell)

        range_order = self._create_range_order_candidate(
            amount=self._oms.book_balance[self._base_asset] * 0.0025,
            lower_price=pool_price - 1 * self._target_spread,
            upper_price=pool_price + 1 * self._target_spread,
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

    async def send_orders(self):
        """
        send orders to Chainflip
        """
        try:
            self.open_orders()
            if len(self._limit_order_candidates) > 0 or len(self._range_order_candidates) > 0:
                logger.info(f'send_orders: awaiting cancellation of open orders')
                await self.cancel_orders()

            self._create_orders()
            await self._oms.send_limit_orders(self._limit_order_candidates)
            await self._oms.send_range_orders(self._range_order_candidates)

        except Exception as e:
            logger.exception(f'Error sending orders" {e}')

    async def update_order_book(self):
        """
        get latest order book
        """
        try:
            await self._order_book.update()
        except Exception as e:
            logger.exception(f'Error updating order book: {e}')

    async def update_pool_fees(self):
        """
        update pool fees
        """
        try:
            await self._pools.update_pool_fees()
        except Exception as e:
            logger.exception(f'Error updating pool fees: {e}')

    async def start_pools_websocket(self):
        """
        start pool websocket for price updates
        """
        try:
            await self._pools.start_pool_stream()

        except Exception as e:
            logger.exception(f'Error starting pools price websocket: {e}')

    async def start_chainflip_update_stream(self):
        """
        start chainflip websocket for updates
        """
        try:
            await self._chainflip_updates_stream.start_websocket()

        except Exception as e:
            logger.exception(f'Error starting Chainflip update stream: {e}')

    async def sleep(self, time: int = None):
        if time is None:
            await asyncio.sleep(self._order_time - 2)
        else:
            await asyncio.sleep(time)

    async def run_strategy(self):
        """
        Entry Point to the strategy.
        Very simple flow of events. Edit as you require.
        """
        logger.info(f'Initialised strategy: steaming quotes for {self._order_time} seconds')
        logger.info(f'Strategy will sleep for 10 seconds to allow data to be pulled')
        await self.update_pool_fees()
        await self.start_pools_websocket()
        await self.update_order_book()
        await self._oms.check_order_book_and_cancel(self._order_book.open_lp_orders)
        await self.start_chainflip_update_stream()
        await self.sleep(10)
        while True:
            await self._oms.get_asset_balances()
            await self.update_order_book()
            await self._oms.check_order_book_and_cancel(self._order_book.open_lp_orders)
            self._order_book.open_lp_orders.clear()
            await self.sleep(2)
            await self.send_orders()
            await self.update_order_book()
            await self.sleep()
            await self.cancel_orders()
            await self.update_order_book()
            await self.sleep(2)
            self._limit_order_candidates.clear()
            self._range_order_candidates.clear()
