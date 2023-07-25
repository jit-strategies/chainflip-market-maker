import aiohttp

from typing import Optional

import chainflip_partnernet.utils.format as formatter
import chainflip_partnernet.utils.logger as log

from chainflip_partnernet.utils.constants import CommandMap, Side

logger = log.setup_custom_logger('root')


class SendCommand:
    """
    Chainflip partnernet commands.
    """
    def __init__(self, set_id: str = ""):
        self._id = set_id
        self._response: Optional[dict] = None
        self._commands = {
            CommandMap.Register: self._register_account,
            CommandMap.AssetBalances: self._get_asset_balances,
            CommandMap.WithdrawAsset: self._withdraw_asset,
            CommandMap.LiquidityDeposit: self._liquidity_deposit,
            CommandMap.RangeOrders: self._get_range_orders,
            CommandMap.LimitOrders: self._get_limit_orders,
            CommandMap.MintRangeOrderLiquidity: self._mint_range_order_liquidity,
            CommandMap.MintRangeOrderAssetAmounts: self._mint_range_order_asset_amounts,
            CommandMap.BurnRangeOrder: self._burn_range_order,
            CommandMap.MintLimitOrder: self._mint_limit_order,
            CommandMap.BurnLimitOrder: self._burn_limit_order,
        }
        self._async_client = aiohttp.ClientSession

    async def await_response(self, header: dict, data: dict):
        async with self._async_client(headers=header) as session:
            async with session.post(url='http://localhost:10589', json=data) as response:
                self._response = await response.json()

    async def _register_account(self):
        header = {
            'Content-Type': 'application/json',
        }

        data = {
            'id': self._id,
            'jsonrpc': '2.0',
            'method': 'lp_registerAccount',
            'params': [],
        }

        await self.await_response(header, data)

    async def _get_asset_balances(self):
        header = {
            'Content-Type': 'application/json',
        }

        data = {
            'id': self._id,
            'jsonrpc': '2.0',
            'method': 'lp_assetBalances',
            'params': [],
        }

        await self.await_response(header, data)

    async def _withdraw_asset(self, amount: float, asset: str, address: str = ''):
        formatted_asset = formatter.asset_to_str(asset)
        formatted_amount = formatter.asset_to_amount(formatted_asset, amount)
        header = {
            'Content-Type': 'application/json',
        }

        data = {
            'id': self._id,
            'jsonrpc': '2.0',
            'method': 'lp_withdrawAsset',
            'params': [
                formatted_amount,
                formatted_asset,
                address,
            ],
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
            'method': 'lp_liquidityDeposit',
            'params': [
                formatted_asset,
            ],
        }

        await self.await_response(header, data)

    async def _get_range_orders(self):
        header = {
            'Content-Type': 'application/json',
        }

        data = {
            'id': self._id,
            'jsonrpc': '2.0',
            'method': 'lp_getRangeOrders',
            'params': [],
        }

        await self.await_response(header, data)

    async def _get_limit_orders(self):
        header = {
            'Content-Type': 'application/json',
        }
        data = {
            'id': self._id,
            'jsonrpc': '2.0',
            'method': 'lp_getRangeOrders',
            'params': [],
        }

        await self.await_response(header, data)

    async def _mint_range_order_liquidity(
            self,
            amount: float,
            asset: str,
            price_1: float,
            price_2: float
    ):
        formatted_asset = formatter.asset_to_str(asset)
        formatted_amount = formatter.asset_to_amount(formatted_asset, amount)
        tick_1 = formatter.price_to_tick(asset, price_1)
        tick_2 = formatter.price_to_tick(asset, price_2)
        header = {
            'Content-Type': 'application/json',
        }

        data = {
            'id': self._id,
            'jsonrpc': '2.0',
            'method': 'lp_mintRangeOrder',
            'params': [
                formatted_asset,
                tick_1,
                tick_2,
                {"PoolLiquidity": formatted_amount},
            ],
        }

        await self.await_response(header, data)

    async def _mint_range_order_asset_amounts(
            self,
            amount: float,
            asset: str,
            price_1: float,
            price_2: float,
            minimum_amount: float = None,
            is_amount_unstable: bool = True
    ):
        formatted_asset = formatter.asset_to_str(asset)
        formatted_amount = formatter.asset_to_amount(formatted_asset, amount)
        if minimum_amount is None:
            formatted_minimum = 0
        else:
            formatted_minimum = formatter.asset_to_amount(formatted_asset, minimum_amount)
        tick_1 = formatter.price_to_tick(asset, price_1)
        tick_2 = formatter.price_to_tick(asset, price_2)
        header = {
            'Content-Type': 'application/json',
        }

        if is_amount_unstable:
            data = {
                'id': self._id,
                'jsonrpc': '2.0',
                'method': 'lp_mintRangeOrder',
                'params': [
                    formatted_asset,
                    tick_1,
                    tick_2,
                    {
                        "AssetAmounts":
                        {
                            "desired": {"unstable": formatted_amount, "stable": 0},
                            "minimum": {"unstable": formatted_minimum, "stable": 0}
                        }
                    }
                ],
            }

        else:
            data = {
                'id': self._id,
                'jsonrpc': '2.0',
                'method': 'lp_mintRangeOrder',
                'params': [
                    formatted_asset,
                    tick_1,
                    tick_2,
                    {
                        "AssetAmounts":
                            {
                                "desired": {"unstable": 0, "stable": formatted_amount},
                                "minimum": {"unstable": 0, "stable": formatted_minimum}
                            }
                    }
                ],
            }

        await self.await_response(header, data)

    async def _burn_range_order(
            self,
            amount: float,
            asset: str,
            price_1: float,
            price_2: float
    ):
        formatted_asset = formatter.asset_to_str(asset)
        formatted_amount = formatter.asset_to_amount(formatted_asset, amount)
        tick_1 = formatter.price_to_tick(asset, price_1)
        tick_2 = formatter.price_to_tick(asset, price_2)
        header = {
            'Content-Type': 'application/json',
        }

        data = {
            'id': self._id,
            'jsonrpc': '2.0',
            'method': 'lp_burnRangeOrder',
            'params': [
                formatted_asset,
                tick_1,
                tick_2,
                formatted_amount,
            ],
        }

        await self.await_response(header, data)

    async def _mint_limit_order(
            self,
            amount: float,
            asset: str,
            price: float,
            side: Side = Side.BUY
    ):
        formatted_asset = formatter.asset_to_str(asset)
        formatted_amount = formatter.asset_to_amount(formatted_asset, amount)
        tick = formatter.price_to_tick(asset, price)
        header = {
            'Content-Type': 'application/json',
        }
        data = {
            'id': self._id,
            'jsonrpc': '2.0',
            'method': 'lp_mintLimitOrder',
            'params': [
                formatted_asset,
                side.value[0],
                tick,
                formatted_amount,
            ],
        }

        await self.await_response(header, data)

    async def _burn_limit_order(
            self,
            amount: float,
            asset: str,
            price: float,
            side: Side = Side.BUY
    ):
        formatted_asset = formatter.asset_to_str(asset)
        formatted_amount = formatter.asset_to_amount(formatted_asset, amount)
        tick = formatter.price_to_tick(asset, price)
        header = {
            'Content-Type': 'application/json',
        }

        data = {
            'id': self._id,
            'jsonrpc': '2.0',
            'method': 'lp_burnLimitOrder',
            'params': [
                formatted_asset,
                side.value[0],
                tick,
                formatted_amount,
            ],
        }

        await self.await_response(header, data)

    async def __call__(self, command: CommandMap = CommandMap.Empty, *args):
        await self._commands[command](*args)
        return self._response
