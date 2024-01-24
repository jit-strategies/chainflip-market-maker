import aiohttp

from typing import Optional

import chainflip.utils.format as formatter
import chainflip.utils.logger as log
import chainflip.utils.constants as CONSTANTS

from chainflip.utils.constants import APICommands

logger = log.setup_custom_logger('root')


class ApiCall:
    """
    Chainflip Perseverance API calls.
    """

    def __init__(self, user_id: str):
        self._id = user_id
        self._response: Optional[dict] = None
        self._calls = {
            APICommands.Empty: self._pass,
            APICommands.Register: self._register_account,
            APICommands.LiquidityDeposit: self._liquidity_deposit,
            APICommands.RegisterWithdrawalAddress: self._register_liquidity_refund_address,
            APICommands.WithdrawAsset: self._withdraw_asset,
            APICommands.AssetBalances: self._get_asset_balances,
            APICommands.SetRangeOrderByLiquidity: self._set_range_order_by_liquidity,
            APICommands.SetRangeOrderByAmounts: self._set_range_order_by_asset_amounts,
            APICommands.UpdateLimitOrder: self._update_limit_order,
            APICommands.SetLimitOrder: self._set_limit_order
        }
        self._async_client = aiohttp.ClientSession

    @property
    def response(self) -> Optional[dict]:
        return self._response

    @staticmethod
    def _get_header() -> dict:
        return {
            'Content-Type': 'application/json',
        }
    
    async def await_response(self, header: dict, data: dict):
        async with self._async_client(headers=header) as session:
            async with session.post(url='http://localhost:10589', json=data) as response:
                self._response = await response.json()

    async def _pass(self):
        return

    async def _register_account(self):
        data = {
            'id': self._id,
            'jsonrpc': '2.0',
            'method': 'lp_register_account',
            'params': [],
        }

        await self.await_response(self._get_header(), data)

    async def _liquidity_deposit(self, asset: str):
        formatted_asset = formatter.asset_to_str(asset)

        data = {
            'id': self._id,
            'jsonrpc': '2.0',
            'method': 'lp_liquidity_deposit',
            'params': {
                'asset': formatted_asset
            }
        }

        await self.await_response(self._get_header(), data)

    async def _register_liquidity_refund_address(self, chain: CONSTANTS.Chains, address: str):
        data = {
            'id': self._id,
            'jsonrpc': '2.0',
            'method': 'lp_register_liquidity_refund_address',
            'params': {
                'chain': chain.value,
                'address': address
            }
        }

        await self.await_response(self._get_header(), data)

    async def _get_asset_balances(self):
        data = {
            'id': self._id,
            'jsonrpc': '2.0',
            'method': 'lp_asset_balances',
            'params': [],
        }

        await self.await_response(self._get_header(), data)

    async def _withdraw_asset(self, amount: float, asset: str, address: str = ''):
        formatted_asset = formatter.asset_to_str(asset)
        formatted_amount = formatter.amount_in_asset(formatted_asset, amount)

        data = {
            'id': self._id,
            'jsonrpc': '2.0',
            'method': 'lp_withdraw_asset',
            'params': {
                'asset_amount': formatted_amount,
                'asset': formatted_asset,
                'destination_address': address
            }
        }

        await self.await_response(self._get_header(), data)

    async def _get_open_swapping_channels(self):
        data = {
            'id': self._id,
            'jsonrpc': '2.0',
            'method': 'lp_get_open_swap_channels',
            'params': [],
        }

        await self.await_response(self._get_header(), data)

    async def _set_range_order_by_liquidity(
            self,
            base_asset: str,
            quote_asset: str,
            order_id: int,
            amount: float,
            lower_price: float,
            upper_price: float,
    ):
        if lower_price >= upper_price:
            logger.error(f'ApiCall._set_range_order_by_liquidity:'
                         f'lower_price={lower_price} should be lower than upper_price={upper_price}')
        formatted_base = formatter.asset_to_str(base_asset)
        formatted_quote = formatter.asset_to_str(quote_asset)
        formatted_amount = formatter.amount_in_asset(formatted_base, amount)
        tick_1 = formatter.price_to_tick(lower_price, formatted_base)
        tick_2 = formatter.price_to_tick(upper_price, formatted_base)

        data = {
            'id': self._id,
            'jsonrpc': '2.0',
            'method': 'lp_set_range_order',
            'params': {
                'base_asset': formatted_base,
                'quote_asset': formatted_quote,
                'id': order_id,
                'tick_range': [tick_1, tick_2],
                'size': {'Liquidity': {'liquidity': formatted_amount}}
            }
        }

        await self.await_response(self._get_header(), data)

    async def _set_range_order_by_asset_amounts(
            self,
            base_asset: str,
            quote_asset: str,
            order_id: int,
            max_base_amount: float,
            max_pair_amount: float,
            min_base_amount: float,
            min_pair_amount: float,
            lower_price: float,
            upper_price: float
    ):
        if lower_price >= upper_price:
            logger.error(f'ApiCall._set_range_order_by_asset_amounts:'
                         f'lower_price={lower_price} should be lower than upper_price={upper_price}')

        formatted_max_base_amount = formatter.amount_in_asset(base_asset, max_base_amount)
        formatted_min_base_amount = formatter.amount_in_asset(base_asset, min_base_amount)
        formatted_max_pair_amount = formatter.amount_in_asset(base_asset, max_pair_amount)
        formatted_min_pair_amount = formatter.amount_in_asset(base_asset, min_pair_amount)
        tick_1 = formatter.price_to_tick(lower_price, base_asset)
        tick_2 = formatter.price_to_tick(upper_price, base_asset)

        data = {
            'id': self._id,
            'jsonrpc': '2.0',
            'method': 'lp_set_range_order',
            'params': {
                'base_asset': base_asset,
                'quote_asset': quote_asset,
                'id': order_id,
                'tick_range': [tick_1, tick_2],
                'size_change': {
                    'AssetAmounts': {
                        'maximum': {'base': formatted_max_base_amount, 'pair': formatted_max_pair_amount},
                        'minimum': {'base': formatted_min_base_amount, 'pair': formatted_min_pair_amount}
                    }
                }
            }
        }

        await self.await_response(self._get_header(), data)

    async def _update_limit_order(
            self,
            base_asset: str,
            quote_asset: str,
            side: CONSTANTS.Side,
            order_id: int,
            price: float,
            size_change: CONSTANTS.IncreaseOrDecreaseOrder,
            amount: float,
            wait_for: CONSTANTS.WaitForOption = CONSTANTS.WaitForOption.NO_WAIT,
            dispatch_at: Optional[int] = None
    ):
        """
        If no price is supplied, the order is updated using the original price
        """
        tick = None
        if price:
            tick = formatter.price_to_tick(price, base_asset)

        if side == CONSTANTS.Side.SELL:
            amount = formatter.amount_in_asset(base_asset, amount)
            side = "sell"
        else:
            amount = formatter.amount_in_asset(quote_asset, amount * price)
            side = "buy"

        if dispatch_at:
            data = {
                'id': self._id,
                'jsonrpc': '2.0',
                'method': 'lp_update_limit_order',
                'params': {
                    'base_asset': base_asset,
                    'quote_asset': quote_asset,
                    'side': side,
                    'id': order_id,
                    'tick': tick,
                    'amount_change': {size_change.value: amount},
                    'wait_for': wait_for,
                    'dispatch_at': dispatch_at
                }
            }
        else:
            data = {
                'id': self._id,
                'jsonrpc': '2.0',
                'method': 'lp_update_limit_order',
                'params': {
                    'base_asset': base_asset,
                    'quote_asset': quote_asset,
                    'side': side,
                    'id': order_id,
                    'tick': tick,
                    'amount_change': {size_change.value: amount},
                    'wait_for': wait_for
                }
            }

        await self.await_response(self._get_header(), data)

    async def _set_limit_order(
            self,
            base_asset: str,
            quote_asset: str,
            side: CONSTANTS.Side,
            order_id: int,
            price: float,
            amount: float,
            wait_for: CONSTANTS.WaitForOption = CONSTANTS.WaitForOption.NO_WAIT,
            dispatch_at: Optional[int] = None
    ):
        if side == CONSTANTS.Side.SELL:
            amount = formatter.amount_in_asset(base_asset, amount)
            side = "sell"
        else:
            amount = formatter.amount_in_asset(quote_asset, amount * price)
            side = "buy"
        tick = formatter.price_to_tick(price, base_asset)

        if dispatch_at:
            data = {
                'id': self._id,
                'jsonrpc': '2.0',
                'method': 'lp_set_limit_order',
                'params': {
                    'base_asset': base_asset,
                    'quote_asset': quote_asset,
                    'side': side,
                    'id': order_id,
                    'tick': tick,
                    'sell_amount': amount,
                    'wait_for': wait_for.value,
                    'dispatch_at': dispatch_at
                }
            }
        else:
            data = {
                'id': self._id,
                'jsonrpc': '2.0',
                'method': 'lp_set_limit_order',
                'params': {
                    'base_asset': base_asset,
                    'quote_asset': quote_asset,
                    'side': side,
                    'id': order_id,
                    'tick': tick,
                    'sell_amount': amount,
                    'wait_for': wait_for.value,
                }
            }

        await self.await_response(self._get_header(), data)

    async def __call__(self, api_call: APICommands = APICommands.Empty, *args):
        await self._calls[api_call](*args)
        return self._response
