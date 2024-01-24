import asyncio

import chainflip.utils.logger as log
import chainflip.utils.constants as CONSTANTS
import chainflip.utils.format as formatter

from chainflip.exchange.rpc import RpcCall
from chainflip.exchange.pools import Pool
from chainflip.utils.constants import RPCCommands


logger = log.setup_custom_logger('root')


class ChainflipPools:
    """
    Class object monitoring Chainflip pools.
    """

    def __init__(self, user_id: str,  lp_id: str = None):
        self._id = user_id
        self._lp_id = lp_id
        self._rpc_calls = RpcCall(self._id)
        self._pools = dict()
        self._response = None

    @property
    def pools(self) -> dict:
        return self._pools

    def _log_response(self, command: str):
        """
        logs the response from Chainflip
        """
        logger.info(f'Chainflip v.{CONSTANTS.version}: {command} response: {self._response["result"]}')

    async def _rpc_pool_fees(self, pool: Pool):
        try:
            self._response = await self._rpc_calls(
                RPCCommands.PoolInfo,
                pool.base_asset,
                pool.quote_asset
            )
        except Exception as e:
            logger.error(f'_rpc_pool_fees: {e}')
        self._log_response('_rpc_pool_fees')

    async def _rpc_pool_depth(self, pool: Pool, upper_price: float, lower_price: float):
        try:
            self._response = await self._rpc_calls(
                RPCCommands.PoolDepth,
                pool.base_asset,
                pool.quote_asset,
                lower_price,
                upper_price
            )
        except Exception as e:
            logger.error(f'_rpc_pool_depth: {e}')
        self._log_response('_rpc_pool_depth')

    async def _rpc_pool_liquidity(self, pool: Pool):
        try:
            self._response = await self._rpc_calls(
                RPCCommands.PoolLiquidity,
                pool.base_asset,
                pool.quote_asset
            )
        except Exception as e:
            logger.error(f'_rpc_pool_liquidity: {e}')
        self._log_response('_rpc_pool_liquidity')

    async def _rpc_pool_orders(self, pool: Pool):
        try:
            self._response = await self._rpc_calls(
                RPCCommands.PoolOrders,
                pool.base_asset,
                pool.quote_asset,
            )
        except Exception as e:
            logger.error(f'_rpc_pool_orders: {e}')
        self._log_response('_rpc_pool_orders')

    async def _rpc_pool_range_liquidity_value(self, pool: Pool, lower_price: float, upper_price: float, amount: float):
        try:
            self._response = await self._rpc_calls(
                RPCCommands.PoolRangeOrdersLiquidityValue,
                pool.base_asset,
                pool.quote_asset,
                lower_price,
                upper_price,
                amount
            )
        except Exception as e:
            logger.error(f'_rpc_pool_range_liquidity_value: {e}')
        self._log_response('_rpc_pool_range_liquidity_value')

    async def _update_pool_liquidity(self, pool: Pool):
        """
        update pool liquidity for a given pool
        :param pool: Pool object
        :return
        """
        await self._rpc_pool_liquidity(pool)
        pool.liquidity = self._response['result']

    def add_pool(self, base_asset: str, quote_asset: str):
        """
        add a pool to the observer
        :param base_asset: str for base asset
        :param quote_asset: str for pair asset
        :return
        """
        base_asset = formatter.asset_to_str(base_asset)
        quote_asset = formatter.asset_to_str(quote_asset)
        pool = Pool(base_asset, quote_asset)
        self._pools[f'{base_asset}-{quote_asset}'] = pool
        logger.info(f"Added pool {pool}")

    async def update_pool_fees(self):
        """
        gathers all pools and updates their fees
        :return
        """
        for key in self._pools.keys():
            pool = self._pools[key]
            await self._rpc_pool_fees(pool)
            pool.fees = self._response['result']

    async def update_all_pools(self):
        """
        gathers all pools and updates their liquidity and orders
        :return
        """
        updates = list()
        for key in self._pools.keys():
            updates.append(self._update_pool_liquidity(self._pools[key]))
            # other methods if required

        await asyncio.gather(*updates)

    async def start_pool_stream(self):
        """
        start all pools stream
        :return
        """
        streams = list()
        for key in self._pools.keys():
            pool = self._pools[key]
            logger.info(f'Starting stream for pool price for pool: {pool}')
            streams.append(pool.start_websocket(user_id=self._id))

        await asyncio.gather(*streams)
