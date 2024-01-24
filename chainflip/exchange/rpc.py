import aiohttp

from typing import Optional

import chainflip.utils.format as formatter
import chainflip.utils.logger as log

from chainflip.utils.constants import RPCCommands


logger = log.setup_custom_logger('root')


class RpcCall:
    """
    Chainflip PerseveranceRPC calls.
    """

    def __init__(self, user_id: str):
        self._id = user_id
        self._response: Optional[dict] = None
        self._calls = {
            RPCCommands.Empty: self._pass,
            RPCCommands.AccountInfo: self._get_account_info,
            RPCCommands.PoolInfo: self._get_pool_info,
            RPCCommands.PoolDepth: self._get_pool_depth,
            RPCCommands.PoolLiquidity: self._get_pool_liquidity,
            RPCCommands.PoolOrders: self._get_pool_orders,
            RPCCommands.PoolRangeOrdersLiquidityValue: self._get_pool_range_liquidity_value,
            RPCCommands.RequiredRatioForRangeOrder: self._get_required_asset_ratio_for_range_order
        }
        self._async_client = aiohttp.ClientSession
    
    @staticmethod
    def _get_header() -> dict:
        return {
            'Content-Type': 'application/json',
        }
    
    async def await_response(self, header: dict, data: dict):
        async with self._async_client(headers=header) as session:
            async with session.post(url='http://localhost:9944', json=data) as response:
                self._response = await response.json()

    async def _pass(self):
        pass

    async def _get_account_info(self, account_id: str):
        data = {
            'id': self._id,
            'jsonrpc': '2.0',
            'method': 'cf_account_info',
            'params': {
                'account_id': account_id
            }
        }

        await self.await_response(self._get_header(), data)

    async def _get_required_asset_ratio_for_range_order(
            self,
            base_asset: str,
            quote_asset: str,
            lower_price: float,
            upper_price: float
    ):
        if lower_price >= upper_price:
            logger.error(f'RpcCall._get_required_asset_ratio_for_range_order:'
                         f'lower_price={lower_price} should be lower than upper_price={upper_price}')
        formatted_base = formatter.asset_to_str(base_asset)
        formatted_pair = formatter.asset_to_str(quote_asset)
        tick_1 = formatter.price_to_tick(lower_price, formatted_base)
        tick_2 = formatter.price_to_tick(upper_price, formatted_base)

        data = {
            'id': self._id,
            'jsonrpc': '2.0',
            'method': 'cf_required_asset_ratio_for_range_order',
            'params': {
                'base_asset': formatted_base,
                'quote_asset': formatted_pair,
                'tick_range': [tick_1, tick_2]
            }
        }

        await self.await_response(self._get_header(), data)

    async def _get_pool_info(
            self,
            base_asset: str,
            quote_asset: str
    ):
        formatted_base = formatter.asset_to_str(base_asset)
        formatted_pair = formatter.asset_to_str(quote_asset)
        
        data = {
            'id': self._id,
            'jsonrpc': '2.0',
            'method': 'cf_pool_info',
            'params': {
                'base_asset': formatted_base,
                'quote_asset': formatted_pair
            }
        }

        await self.await_response(self._get_header(), data)

    async def _get_pool_depth(
            self,
            base_asset: str,
            quote_asset: str,
            lower_price: float,
            upper_price: float
    ):
        if lower_price >= upper_price:
            logger.error(f'RpcCall._get_pool_depth:'
                         f'lower_price={lower_price} should be lower than upper_price={upper_price}')
        formatted_base = formatter.asset_to_str(base_asset)
        formatted_pair = formatter.asset_to_str(quote_asset)
        tick_1 = formatter.price_to_tick(lower_price, formatted_base)
        tick_2 = formatter.price_to_tick(upper_price, formatted_base)

        data = {
            'id': self._id,
            'jsonrpc': '2.0',
            'method': 'cf_pool_depth',
            'params':  {
                'base_asset': formatted_base,
                'quote_asset': formatted_pair,
                'tick_range': [tick_1, tick_2]
            }
        }

        await self.await_response(self._get_header(), data)

    async def _get_pool_liquidity(
            self,
            base_asset: str,
            quote_asset: str
    ):
        formatted_base = formatter.asset_to_str(base_asset)
        formatted_pair = formatter.asset_to_str(quote_asset)

        data = {
            'id': self._id,
            'jsonrpc': '2.0',
            'method': 'cf_pool_liquidity',
            'params': {
                'base_asset': formatted_base,
                'quote_asset': formatted_pair,
            }
        }

        await self.await_response(self._get_header(), data)

    async def _get_pool_orders(
            self,
            base_asset: str,
            quote_asset: str,
    ):
        formatted_base = formatter.asset_to_str(base_asset)
        formatted_pair = formatter.asset_to_str(quote_asset)

        data = {
            'id': self._id,
            'jsonrpc': '2.0',
            'method': 'cf_pool_orders',
            'params': {
                'base_asset': formatted_base,
                'quote_asset': formatted_pair,
            }
        }

        await self.await_response(self._get_header(), data)

    async def _get_pool_range_liquidity_value(
            self,
            base_asset: str,
            quote_asset: str,
            lower_price: float,
            upper_price: float,
            amount: float
    ):
        if lower_price >= upper_price:
            logger.error(f'RpcCall._get_pool_range_liquidity_value:'
                         f'lower_price={lower_price} should be lower than upper_price={upper_price}')
        formatted_base = formatter.asset_to_str(base_asset)
        formatted_pair = formatter.asset_to_str(quote_asset)
        tick_1 = formatter.price_to_tick(lower_price, formatted_base)
        tick_2 = formatter.price_to_tick(upper_price, formatted_base)
        amount = formatter.amount_in_asset(formatted_base, amount)

        data = {
            'id': self._id,
            'jsonrpc': '2.0',
            'method': 'cf_pool_orders',
            'params': {
                'base_asset': formatted_base,
                'quote_asset': formatted_pair,
                'tick_range': [tick_1, tick_2],
                'liquidity': amount
            }
        }

        await self.await_response(self._get_header(), data)

    async def __call__(self, rpc_call: RPCCommands = RPCCommands.Empty, *args):
        await self._calls[rpc_call](*args)
        return self._response
