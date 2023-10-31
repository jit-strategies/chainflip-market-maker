import aiohttp

from typing import Optional

import chainflip_perseverance.utils.format as formatter
import chainflip_perseverance.utils.logger as log

from chainflip_perseverance.utils.constants import APICommands, Chains, IncreaseOrDecreaseOrder


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
            APICommands.UpdateRangeOrderByLiquidity: self._update_range_order_by_liquidity,
            APICommands.UpdateRangeOrderByAmounts: self._update_range_order_by_asset_amounts,
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
    def _format_optional_prices(asset: str, price_1: float, price_2: float) -> Optional[tuple]:
        if price_1 is None or price_2 is None:
            return

        tick_1 = formatter.price_to_tick(price_1, asset)
        tick_2 = formatter.price_to_tick(price_2, asset)

        return tick_1, tick_2

    async def await_response(self, header: dict, data: dict):
        async with self._async_client(headers=header) as session:
            async with session.post(url='http://localhost:10589', json=data) as response:
                self._response = await response.json()

    async def _pass(self):
        return

    async def _register_account(self):
        header = {
            'Content-Type': 'application/json',
        }

        data = {
            'id': self._id,
            'jsonrpc': '2.0',
            'method': 'lp_register_account',
            'params': [],
        }

        await self.await_response(header, data)

    async def _liquidity_deposit(self, asset: str):
        formatted_asset = formatter.asset_to_str(asset)
        header = {
            'Content-Type': 'application/json',
        }

        data = {
            'id': self._id,
            'jsonrpc': '2.0',
            'method': 'lp_liquidity_deposit',
            'params': [
                formatted_asset,
            ],
        }

        await self.await_response(header, data)

    async def _register_liquidity_refund_address(self, chain: Chains, address: str):
        header = {
            'Content-Type': 'application/json',
        }

        data = {
            'id': self._id,
            'jsonrpc': '2.0',
            'method': 'lp_register_liquidity_refund_address',
            'params': [
                chain.value,
                address
            ]
        }

        await self.await_response(header, data)

    async def _get_asset_balances(self):
        header = {
            'Content-Type': 'application/json',
        }

        data = {
            'id': self._id,
            'jsonrpc': '2.0',
            'method': 'lp_asset_balances',
            'params': [],
        }

        await self.await_response(header, data)

    async def _withdraw_asset(self, amount: float, asset: str, address: str = ''):
        formatted_asset = formatter.asset_to_str(asset)
        formatted_amount = formatter.amount_in_asset(formatted_asset, amount)
        header = {
            'Content-Type': 'application/json',
        }

        data = {
            'id': self._id,
            'jsonrpc': '2.0',
            'method': 'lp_withdraw_asset',
            'params': [
                formatted_amount,
                formatted_asset,
                address,
            ],
        }

        await self.await_response(header, data)

    async def _get_open_swapping_channels(self):
        header = {
            'Content-Type': 'application/json',
        }

        data = {
            'id': self._id,
            'jsonrpc': '2.0',
            'method': 'lp_get_open_swap_channels',
            'params': [],
        }

        await self.await_response(header, data)

    async def _update_range_order_by_liquidity(
            self,
            base_asset: str,
            pair_asset: str,
            order_id: int,
            size: IncreaseOrDecreaseOrder,
            amount: float,
            lower_price: Optional[float] = None,
            upper_price: Optional[float] = None,
    ):
        if lower_price >= upper_price:
            logger.error(f'ApiCall._update_range_order_by_liquidity:'
                         f'lower_price={lower_price} should be lower than upper_price={upper_price}')
        formatted_base = formatter.asset_to_str(base_asset)
        formatted_pair = formatter.asset_to_str(pair_asset)
        formatted_amount = formatter.amount_in_asset('USDC', amount)
        header = {
            'Content-Type': 'application/json',
        }

        tick_1, tick_2 = self._format_optional_prices(base_asset, lower_price, upper_price)

        if tick_1 is None and tick_2 is None:
            data = {
                'id': self._id,
                'jsonrpc': '2.0',
                'method': 'lp_update_range_order',
                'params': [
                    formatted_base,
                    formatted_pair,
                    order_id,
                    size.value,
                    {'Liquidity': {'liquidity': formatted_amount}}
                ]
            }

        elif tick_1 is not None and tick_2 is not None:
            data = {
                'id': self._id,
                'jsonrpc': '2.0',
                'method': 'lp_update_range_order',
                'params': [
                    formatted_base,
                    formatted_pair,
                    order_id,
                    size.value,
                    [tick_1, tick_2],
                    {'Liquidity': {'liquidity': formatted_amount}}
                ]
            }

        else:
            logger.error(f'ApiCall._update_range_order_by_liquidity: '
                         f'tick_1={tick_1} and tick_2={tick_2} should both be none or both be a number')
            return

        await self.await_response(header, data)

    async def _update_range_order_by_asset_amounts(
            self,
            base_asset: str,
            pair_asset: str,
            order_id: int,
            increase_or_decrease: IncreaseOrDecreaseOrder,
            max_base_amount: float,
            max_pair_amount: float,
            min_base_amount: float,
            min_pair_amount: float,
            lower_price: float = None,
            upper_price: float = None
    ):
        if lower_price >= upper_price:
            logger.error(f'ApiCall._update_range_order_by_asset_amounts:'
                         f'lower_price={lower_price} should be lower than upper_price={upper_price}')
        formatted_base = formatter.asset_to_str(base_asset)
        formatted_pair = formatter.asset_to_str(pair_asset)
        formatted_max_base_amount = formatter.amount_in_asset(formatted_base, max_base_amount)
        formatted_min_base_amount = formatter.amount_in_asset(formatted_base, min_base_amount)
        formatted_max_pair_amount = formatter.amount_in_asset(formatted_pair, max_pair_amount)
        formatted_min_pair_amount = formatter.amount_in_asset(formatted_pair, min_pair_amount)
        header = {
            'Content-Type': 'application/json',
        }

        tick_1, tick_2 = self._format_optional_prices(base_asset, lower_price, upper_price)

        if tick_1 is None and tick_2 is None:
            data = {
                'id': self._id,
                'jsonrpc': '2.0',
                'method': 'lp_update_range_order',
                'params': [
                    formatted_base,
                    formatted_pair,
                    order_id,
                    increase_or_decrease.value,
                    {'AssetAmounts': {
                        'maximum': {'base': formatted_max_base_amount, 'pair': formatted_max_pair_amount},
                        'minimum': {'base': formatted_min_base_amount, 'pair': formatted_min_pair_amount}
                    }}
                ]
            }

        elif tick_1 is not None and tick_2 is not None:
            data = {
                'id': self._id,
                'jsonrpc': '2.0',
                'method': 'lp_update_range_order',
                'params': [
                    formatted_base,
                    formatted_pair,
                    order_id,
                    increase_or_decrease.value,
                    [tick_1, tick_2],
                    {'AssetAmounts': {
                        'maximum': {'base': formatted_max_base_amount, 'pair': formatted_max_pair_amount},
                        'minimum': {'base': formatted_min_base_amount, 'pair': formatted_min_pair_amount}
                    }}
                ]
            }

        else:
            raise logger.error(f'ApiCall._update_range_order_by_asset_amounts: '
                               f'tick_1={tick_1} and tick_2={tick_2} should both be none or both be a number')

        await self.await_response(header, data)

    async def _set_range_order_by_liquidity(
            self,
            base_asset: str,
            pair_asset: str,
            order_id: int,
            amount: float,
            lower_price: float,
            upper_price: float,
    ):
        if lower_price >= upper_price:
            logger.error(f'ApiCall._set_range_order_by_liquidity:'
                         f'lower_price={lower_price} should be lower than upper_price={upper_price}')
        formatted_base = formatter.asset_to_str(base_asset)
        formatted_pair = formatter.asset_to_str(pair_asset)
        formatted_amount = formatter.amount_in_asset(formatted_base, amount)
        tick_1 = formatter.price_to_tick(lower_price, formatted_base)
        tick_2 = formatter.price_to_tick(upper_price, formatted_base)
        header = {
            'Content-Type': 'application/json',
        }

        data = {
            'id': self._id,
            'jsonrpc': '2.0',
            'method': 'lp_set_range_order',
            'params': [
                formatted_base,
                formatted_pair,
                order_id,
                [tick_1, tick_2],
                {'Liquidity': {'liquidity': formatted_amount}}
            ],
        }

        await self.await_response(header, data)

    async def _set_range_order_by_asset_amounts(
            self,
            base_asset: str,
            pair_asset: str,
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
        formatted_base = formatter.asset_to_str(base_asset)
        formatted_pair = formatter.asset_to_str(pair_asset)
        formatted_max_base_amount = formatter.amount_in_asset(formatted_base, max_base_amount)
        formatted_min_base_amount = formatter.amount_in_asset(formatted_base, min_base_amount)
        formatted_max_pair_amount = formatter.amount_in_asset(formatted_base, max_pair_amount)
        formatted_min_pair_amount = formatter.amount_in_asset(formatted_base, min_pair_amount)
        tick_1 = formatter.price_to_tick(lower_price, formatted_base)
        tick_2 = formatter.price_to_tick(upper_price, formatted_base)
        header = {
            'Content-Type': 'application/json',
        }

        data = {
            'id': self._id,
            'jsonrpc': '2.0',
            'method': 'lp_set_range_order',
            'params': [
                formatted_base,
                formatted_pair,
                order_id,
                [tick_1, tick_2],
                {'AssetAmounts': {
                    'maximum': {'base': formatted_max_base_amount, 'pair': formatted_max_pair_amount},
                    'minimum': {'base': formatted_min_base_amount, 'pair': formatted_min_pair_amount}
                }}
            ]
        }

        await self.await_response(header, data)

    async def _update_limit_order(
            self,
            sold_asset: str,
            buy_asset: str,
            order_id: int,
            price: Optional[float],
            increase_or_decrease: IncreaseOrDecreaseOrder,
            amount: float
    ):
        """
        If no price is supplied, the order is updated using the original price

        """
        formatted_sold = formatter.asset_to_str(sold_asset)
        formatted_buy = formatter.asset_to_str(buy_asset)
        tick = None
        if price:
            tick = formatter.price_to_tick(price, formatted_sold)
        formatted_amount = formatter.amount_in_asset(formatted_sold, amount)
        header = {
            'Content-Type': 'application/json',
        }

        if tick is None:
            data = {
                'id': self._id,
                'jsonrpc': '2.0',
                'method': 'lp_update_limit_order',
                'params': [
                    formatted_sold,
                    formatted_buy,
                    order_id,
                    increase_or_decrease.value,
                    formatted_amount
                ]
            }
        else:
            data = {
                'id': self._id,
                'jsonrpc': '2.0',
                'method': 'lp_update_limit_order',
                'params': [
                    formatted_sold,
                    formatted_buy,
                    order_id,
                    tick,
                    formatted_amount
                ]
            }

        await self.await_response(header, data)

    async def _set_limit_order(
            self,
            sold_asset: str,
            buy_asset: str,
            order_id: int,
            price: float,
            amount: float
    ):
        formatted_sold = formatter.asset_to_str(sold_asset)
        formatted_buy = formatter.asset_to_str(buy_asset)
        formatted_amount = formatter.amount_in_asset(formatted_sold, amount)
        tick = formatter.price_to_tick(price, formatted_sold)

        header = {
            'Content-Type': 'application/json',
        }
        data = {
                'id': self._id,
                'jsonrpc': '2.0',
                'method': 'lp_set_limit_order',
                'params': [
                    formatted_sold,
                    formatted_buy,
                    order_id,
                    tick,
                    formatted_amount
                ]
            }

        await self.await_response(header, data)

    async def __call__(self, api_call: APICommands = APICommands.Empty, *args):
        await self._calls[api_call](*args)
        return self._response
