import asyncio

import chainflip_perseverance.utils.constants as CONSTANTS
import chainflip_perseverance.utils.format as formatter
import chainflip_perseverance.utils.logger as log

from chainflip_perseverance.utils.data_types import LimitOrder, RangeOrder
from chainflip_perseverance.market_maker.market_maker import OMS
from chainflip_perseverance.market_maker.perseverance_pools import PerseverancePools
from chainflip_perseverance.market_maker.prewitness_swaps import Prewitnesser

logger = log.setup_custom_logger('root')


class StrategyJIT:
    """
    Just In Time strategy.
    Monitor the prewitnessed swaps (swaps seen by Chainflip Chain that MAY be executed in a number of blocks time).
    When a swap is seen, create a limit order and ranged order with a given price.
    After the swap has occurred delete both orders.
    """

    def __init__(
            self,
            base_asset: str,
            pair_asset: str,
            data_feed: dict,
            oms: OMS,
            perseverance_pools: PerseverancePools,
            prewitnesser: Prewitnesser
    ):
        self._base_asset = formatter.asset_to_str(base_asset)
        self._pair_asset = formatter.asset_to_str(pair_asset)
        self._data = data_feed
        self._oms = oms
        self._pools = perseverance_pools
        self._prewitnesser = prewitnesser
        self._order_id = 0
        self._target_fill = 0.1  # 10 % of the swap amount
        self._target_spread = 0.01
        self._jit_swaps_buy = list()
        self._jit_swaps_sell = list()
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

    async def _create_buy_orders(self, amount: int, asset_price: float):
        """
        create buy orders for base_asset, sell pair_asset
        """
        available_amount = self._oms.book_balance[self._pair_asset]
        fill_amount = amount * self._target_fill
        if available_amount > fill_amount:
            self._limit_order_candidates.append(
                self._create_limit_order_candidate(
                    amount=fill_amount,
                    price=asset_price - (asset_price * 0.01),
                    side=CONSTANTS.Side.BUY
                )
            )
        else:
            logger.info(f'Not enough liquidity ({available_amount}) for fill target ({fill_amount})')

    async def _create_sell_orders(self, amount: int, asset_price: float):
        """
        create sell orders for base asset, buy pair_asset
        """
        available_amount = self._oms.book_balance[self._base_asset]
        fill_amount = amount * self._target_fill
        if available_amount > fill_amount:
            self._limit_order_candidates.append(
                self._create_limit_order_candidate(
                    amount=fill_amount,
                    price=asset_price + (asset_price * 0.01),
                    side=CONSTANTS.Side.SELL
                )
            )
        else:
            logger.info(f'Not enough liquidity ({available_amount}) for fill target ({fill_amount})')

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

    async def send_buy_order(self, amount: int):
        """
        send buy orders to Perseverance for the asset
        """
        try:
            asset_price = self._data[self._base_asset].data.close
        except:
            logger.info(f'_create_orders: strategy waiting on data from binance for asset: {self._base_asset}')
            return

        pool_price = self._pools.pools[f'{self._base_asset}-{self._pair_asset}'].price
        logger.info(
            f'Current pool price for asset {self._base_asset}: {pool_price}, current market price: {asset_price}'
        )

        await self._create_buy_orders(amount, asset_price)
        await self._oms.send_limit_orders(self._limit_order_candidates)

    async def send_sell_order(self, amount: int):
        """
        send sell orders to Perseverance for the asset
        """
        try:
            asset_price = self._data[self._base_asset].data.close
        except:
            logger.info(f'_create_orders: strategy waiting on data from binance for asset: {self._base_asset}')
            return

        pool_price = self._pools.pools[f'{self._base_asset}-{self._pair_asset}'].price
        logger.info(
            f'Current pool price for asset {self._base_asset}: {pool_price}, current market price: {asset_price}'
        )

        await self._create_sell_orders(amount, asset_price)
        await self._oms.send_limit_orders(self._limit_order_candidates)

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

    async def get_incoming_swaps_for_asset(self):
        """
        get the swaps expiring for the asset pair
        """
        self._jit_swaps_buy = await self._prewitnesser.get_swaps(self._base_asset, self._pair_asset)
        self._jit_swaps_sell = await self._prewitnesser.get_swaps(self._pair_asset, self._base_asset)

    async def process_buy_swaps(self):
        """
        attempt to submit limit orders for pre witnessed buy swaps
        """
        for buy in self._jit_swaps_buy:
            await self.send_sell_order(buy.amount)

    async def process_sell_swaps(self):
        """
        attempt to submit limit orders for pre witnessed sell swaps
        """
        for sell in self._jit_swaps_sell:
            await self.send_buy_order(sell.amount)

    async def pull_updates(self):
        await self._oms.get_asset_balances()
        await self.update_pools()
        await self.get_incoming_swaps_for_asset()

    @staticmethod
    async def sleep(time: int = None):
        if time is None:
            await asyncio.sleep(1)
        else:
            await asyncio.sleep(time)

    async def run_strategy(self):
        logger.info(f'Initialised strategy: Just in Time liquidity')
        logger.info(f'Strategy will sleep for 30 seconds to allow data to be pulled')
        await self._prewitnesser.add_prewitness_stream(base_asset='Eth', pair_asset='Usdc')
        await self._prewitnesser.add_prewitness_stream(base_asset='Usdc', pair_asset='Eth')
        await self.update_pool_fees()
        await self.start_pools_websocket()
        await self.sleep(5)
        while True:
            await self.pull_updates()
            if len(self._jit_swaps_buy) == 0 and len(self._jit_swaps_sell) == 0:
                await self.sleep(6)
            else:
                logger.info(f'Swap prewitnessed')
                await self.process_buy_swaps()
                await self.process_sell_swaps()
                if len(self._limit_order_candidates) == 0:
                    continue
                else:
                    await self.sleep(7)
                    await self.cancel_orders()
                    self._limit_order_candidates.clear()
                    self._range_order_candidates.clear()
