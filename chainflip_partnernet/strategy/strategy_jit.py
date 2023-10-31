import asyncio

import chainflip_partnernet.utils.constants as CONSTANTS
import chainflip_partnernet.utils.format as formatter
import chainflip_partnernet.utils.logger as log
from chainflip_partnernet.external_env.mem_pools import MemPool
from chainflip_partnernet.utils.data_types import LimitOrder, RangeOrder

from chainflip_partnernet.utils.data_types import BinanceKline
from chainflip_partnernet.external_env.data_stream import BinanceDataFeed
from chainflip_partnernet.chainflip_env.pool import Pool
from chainflip_partnernet.market_maker.market_maker import MarketMaker


logger = log.setup_custom_logger('root')


class StrategyJIT:
    """
    Just In Time strategy.
    Watch for Chainflip Swapping channels to be opened and monitor these addresses on the asset's chain mempool
    When a mempool deposit is witnessed, mint a limit and range order with a chosen price.
    After the AMM has swapped, burn both assets
    """
    def __init__(
            self,
            base_asset: str,
            base_liquidity: float,
            quote_asset: str,
            quote_liquidity: float,
            data_feed: BinanceDataFeed,
            pool: Pool,
            market_maker: MarketMaker,
            mem_pool: MemPool
    ):
        self._base_liquidity = base_liquidity
        self._quote_liquidity = quote_liquidity
        self._base_asset = formatter.asset_to_str(base_asset)
        self._quote_asset = formatter.asset_to_str(quote_asset)
        self._data = data_feed
        self._pool = pool
        self._market_maker = market_maker
        self._mem_pool = mem_pool
        self._limit_order_buy = None
        self._limit_order_sell = None
        self._range_order = None
        self._order_active_time = 12
        self._active_orders = []

    @property
    def liquidity(self) -> tuple:
        return self._base_liquidity, self._quote_liquidity

    @property
    def asset(self) -> str:
        return f'{self._base_asset}-{self._quote_asset}'

    @property
    def data(self) -> BinanceKline:
        return self._data.data

    def _create_limit_order_candidate(self, amount: float, price: float, side: CONSTANTS.Side):
        if side == CONSTANTS.Side.BUY:
            asset = self._quote_asset
            self._limit_order_buy = LimitOrder(amount, price, side, asset)
            logger.info(f"Created buy limit order candidate: {self._limit_order_buy}")
            return
        elif side == CONSTANTS.Side.SELL:
            asset = self._base_asset
            self._limit_order_sell = LimitOrder(amount, price, side, asset)
            logger.info(f"Created sell limit order candidate: {self._limit_order_sell}")
            return
        else:
            logger.error(f'Side is incorrectly set for limit order: {side}')
            return

    def _create_range_order_candidate(self, amount: float, lower_price: float, upper_price: float):
        self._range_order = RangeOrder(amount, lower_price, upper_price, self._quote_asset)
        logger.info(f"Created range order candidate: {self._range_order}")

    async def send_orders(self):
        try:
            current_price = self._data.data.close
        except:
            logger.info('Strategy waiting on data from binance')
            await self.sleep()
            return

        pool_price = self._pool.pool_price
        current_price = self._data.data.close

        logger.info(f'Current pool price: {pool_price}, current market price: {current_price}')
        if self._mem_pool.witnessed:
            self._create_limit_order_candidate(
                amount=0.001, price=current_price + 0.01, side=CONSTANTS.Side.BUY
            )
            await self._market_maker.mint_limit_order(self._limit_order_buy)
            self._base_liquidity -= self._limit_order_buy.amount

            self._create_range_order_candidate(
                amount=0.001, lower_price=pool_price - 10, upper_price=pool_price + 10,
            )
            await self._market_maker.mint_range_order(self._range_order)
            self._base_liquidity -= self._range_order.amount / 2
            self._quote_liquidity -= self._range_order.amount / 2

            logger.info('JIT strategy - will burn orders one block (6 secs) later')
            await self.sleep()
            await self.cancel_orders()
        else:
            logger.info('No deposits witnessed in mempool. Returning')
            return

        logger.info(f'Open limit orders: {self._market_maker.open_limit_orders}')
        logger.info(f'Open range orders: {self._market_maker.open_range_orders}')

    async def cancel_orders(self):
        await self._market_maker.burn_limit_order()
        await self._market_maker.burn_range_order()

        logger.info(f'Open limit orders: {self._market_maker.open_limit_orders}')
        logger.info(f'Open range orders: {self._market_maker.open_range_orders}')

    async def sleep(self):
        await asyncio.sleep(self._order_active_time)

    async def run_strategy(self):
        logger.info(f'Initialised strategy: steaming quotes for 30 seconds')
        await self.sleep()
        while True:
            await self._market_maker.get_asset_balances()
            await self.send_orders()
            await self.sleep()
            await self._market_maker.get_asset_balances()
