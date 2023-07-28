import asyncio

import chainflip_partnernet.utils.constants as CONSTANTS
import chainflip_partnernet.utils.format as formatter
import chainflip_partnernet.utils.logger as log
from chainflip_partnernet.utils.data_types import LimitOrder, RangeOrder

from chainflip_partnernet.utils.data_types import BinanceKline
from chainflip_partnernet.external_env.data_stream import BinanceDataFeed
from chainflip_partnernet.chainflip_env.pool import Pool
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
            base_asset: str,
            base_liquidity: float,
            quote_asset: str,
            quote_liquidity: float,
            data_feed: BinanceDataFeed,
            pool: Pool,
            market_maker: MarketMaker
    ):
        self._base_liquidity = base_liquidity
        self._quote_liquidity = quote_liquidity
        self._base_asset = formatter.asset_to_str(base_asset)
        self._quote_asset = formatter.asset_to_str(quote_asset)
        self._data = data_feed
        self._pool = pool
        self._market_maker = market_maker
        self._limit_order_buy = None
        self._limit_order_sell = None
        self._range_order = None
        self._limit_order_list = list()
        self._range_order_list = list()
        self._order_active_time = 50
        self._active_orders = list()
        self._ping_pong = 0

    @property
    def liquidity(self) -> tuple:
        return self._base_liquidity, self._quote_liquidity

    @property
    def asset(self) -> str:
        return f'{self._base_asset}-{self._quote_asset}'

    @property
    def data(self) -> BinanceKline:
        return self._data.data

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

    def _create_orders(self):
        pool_price = self._pool.pool_price
        current_price = self._data.data.close

        logger.info(f'Current pool price: {pool_price}, current market price: {current_price}')

        if self._ping_pong % 2 == 0:
            self._create_limit_order_candidate(
                amount=0.00000000001, price=current_price - 0.1, side=CONSTANTS.Side.BUY
            )
            self._limit_order_list.append(self._limit_order_buy)
            self._quote_liquidity -= self._limit_order_buy.amount
        else:
            self._create_limit_order_candidate(
                amount=0.00000000001, price=current_price + 0.1, side=CONSTANTS.Side.SELL
            )
            self._limit_order_list.append(self._limit_order_sell)
            self._base_liquidity -= self._limit_order_sell.amount

        self._create_range_order_candidate(
            amount=0.00000001,
            lower_price=pool_price - 10,
            upper_price=pool_price + 10,
            minimum_amount=None,
            order_type=CONSTANTS.RangeOrderType.LIQUIDITY
        )
        self._range_order_list.append(self._range_order)
        self._base_liquidity -= self._range_order.amount / 2
        self._quote_liquidity -= self._range_order.amount / 2

    async def send_orders(self):
        self.open_orders()
        self._limit_order_list.clear()
        self._range_order_list.clear()
        try:
            self._data.data.close
        except:
            logger.info('Strategy waiting on data from binance')
            await self.sleep()

        self._create_orders()
        asyncio.create_task(self._market_maker.send_limit_orders(self._limit_order_list))
        asyncio.create_task(self._market_maker.send_range_orders(self._range_order_list))

        self._ping_pong += 1

    async def cancel_orders(self):
        self.open_orders()
        await self._market_maker.burn_limit_order()
        await self._market_maker.burn_range_order()

    async def sleep(self):
        await asyncio.sleep(self._order_active_time)

    async def run_strategy(self):
        logger.info(f'Initialised strategy: steaming quotes for 30 seconds')
        await self.sleep()
        while True:
            if len(self._market_maker.open_limit_orders) > 0 or len(self._market_maker.open_range_orders) > 0:
                await self.cancel_orders()
            await self._market_maker.get_asset_balances()
            await self.send_orders()
            await self.sleep()
            await self._market_maker.get_asset_balances()
            await self.cancel_orders()
