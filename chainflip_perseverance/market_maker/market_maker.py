import asyncio
import time

from datetime import datetime
from typing import Union, Optional

import chainflip_perseverance.utils.logger as log
import chainflip_perseverance.utils.constants as CONSTANTS
import chainflip_perseverance.utils.format as formatter

from chainflip_perseverance.utils.constants import APICommands
from chainflip_perseverance.market_maker.order_book import OrderBook
from chainflip_perseverance.perseverance.api import ApiCall
from chainflip_perseverance.utils.data_types import LimitOrder, RangeOrder


logger = log.setup_custom_logger('root')


class OMS:
    """
    Simple order management system class handler.
    """

    def __init__(
            self,
            market_maker_id: str,
            erc20_withdrawal_address: Optional[str] = None,
            btc_withdrawal_address: Optional[str] = None,
            dot_withdrawal_address: Optional[str] = None
    ):
        self._id = market_maker_id
        self._api_calls = ApiCall(user_id=self._id)
        self._order_book = OrderBook()
        self._response = None
        self._withdrawal_addresses = {
            'Eth': erc20_withdrawal_address,
            'Btc': btc_withdrawal_address,
            'Dot': dot_withdrawal_address,
            'Flip': erc20_withdrawal_address,
            'Usdc': erc20_withdrawal_address
        }
        logger.info(f'Initialised Market Maker with id: {self._id}')

    @property
    def open_limit_orders(self) -> dict:
        return self._order_book.limit_orders

    @property
    def open_range_orders(self) -> dict:
        return self._order_book.range_orders

    @property
    def book_balance(self) -> dict:
        return self._order_book.balance

    async def _api_set_limit_order(self, limit_order: LimitOrder):
        try:
            if limit_order.side.name == CONSTANTS.Side.BUY:
                self._response = await self._api_calls(
                    APICommands.SetLimitOrder,
                    limit_order.pair_asset,
                    limit_order.base_asset,
                    limit_order.id,
                    limit_order.price,
                    limit_order.amount
                )
            elif limit_order.side.name == CONSTANTS.Side.SELL:
                self._response = await self._api_calls(
                    APICommands.SetLimitOrder,
                    limit_order.base_asset,
                    limit_order.pair_asset,
                    limit_order.id,
                    limit_order.price,
                    limit_order.amount
                )
            limit_order.timestamp = time.time()
        except Exception as e:
            logger.error(f'_api_set_limit_order: {e}')

    async def _api_set_range_order(self, range_order: RangeOrder):
        try:
            if range_order.type.value == CONSTANTS.RangeOrderType.LIQUIDITY.value:
                self._response = await self._api_calls(
                    APICommands.SetRangeOrderByLiquidity,
                    range_order.base_asset,
                    range_order.pair_asset,
                    range_order.id,
                    range_order.amount,
                    range_order.lower_price,
                    range_order.upper_price
                )
            else:
                self._response = await self._api_calls(
                    APICommands.SetRangeOrderByAmounts,
                    range_order.base_asset,
                    range_order.pair_asset,
                    range_order.id,
                    range_order.max_amounts[0],
                    range_order.max_amounts[1],
                    range_order.min_amounts[0],
                    range_order.min_amounts[1],
                    range_order.lower_price,
                    range_order.upper_price
                )
            range_order.timestamp = time.time()
        except Exception as e:
            logger.error(f'_api_set_range_order: {e}')

    def _log_response(self):
        """
        logs the response from Chainflip Perseverance
        :return:
        """
        logger.info(f'Chainflip v.{CONSTANTS.version} response: {self._response["result"]}')

    def _check_for_error_response(self, function_name: str) -> bool:
        """
        check for an error from the Chainflip Perseverance and log it
        :param function_name: str for where the call originated from
        :return: boolean
        """
        if 'error' in self._response:
            logger.error(f'{function_name}: {self._response["error"]["message"]}')
            return True
        else:
            return False

    async def get_asset_balances(self):
        """
        get current LP balances on the Chainflip Perseverance, updates balances and logs response
        :return:
        """
        logger.info(f'Chainflip v.{CONSTANTS.version}: asset balances')
        self._response = await self._api_calls(APICommands.AssetBalances)
        if self._check_for_error_response(function_name='get_asset_balances'):
            return
        self._order_book.update_balance(formatter.deserialize_balance(self._response))
        logger.info(f'Current asset balances: {self.book_balance}')

    async def withdraw_asset(self, asset: str, amount: Union[float, int] = 10000000):
        """
        withdraw assets from Chainflip Perseverance. Asset is withdrawn to set wallets provided in the OMS class.
        :param asset: the asset you wish to withdraw
        :param amount: the amount you wish to withdraw. If left empty, it will default to a large int to withdraw all.
        """
        self._response = self._api_calls(
            APICommands.WithdrawAsset,
            amount, asset, self._withdrawal_addresses[asset]
        )

    async def create_new_limit_order(self, limit_order: LimitOrder):
        """
        create (mint) a limit order on Chainflip Perseverance.
        :param limit_order: LimitOrder type
        """
        logger.info(f'Chainflip v.{CONSTANTS.version}: creating limit order - {limit_order}')
        await self._api_set_limit_order(limit_order)

        if self._check_for_error_response(function_name='create_limit_order'):
            return
        if self._response:
            limit_order.timestamp = datetime.now()
            try:
                self._order_book.add_limit_order(limit_order)
                logger.info(f'Created new limit order: id={limit_order.id}')
            except Exception as e:
                logger.error(f'create_limit_order: {e}')
        self._log_response()

    async def delete_limit_order(self, limit_order: LimitOrder):
        """
        delete (burn) a limit order on Chainflip Perseverance.
        :param limit_order: LimitOrder type
        """
        try:
            limit_order = self._order_book.get_limit_order_by_key(limit_order.id)
        except KeyError:
            logger.error(f"delete_limit_order: Attempting to delete limit order id={limit_order.id} not in order book")

        limit_order.amount = 0
        await self._api_set_limit_order(limit_order)

        if self._check_for_error_response(function_name='delete_limit_order'):
            return
        if self._response:
            try:
                self._order_book.remove_limit_order_by_key(limit_order.id)
            except Exception as e:
                logger.error(f'delete_limit_order {e}')
                return

            logger.info(f'Limit order deleted: {limit_order.id}')
        self._log_response()

    async def update_limit_order(self,
                                 limit_order: LimitOrder,
                                 price: Optional[float] = None,
                                 amount: Optional[float] = None):
        """
        update a limit order on Chainflip Perseverance with a new price and / or a new amount.
        this method replaces the order with the same id
        :param limit_order: LimitOrder type
        :param price: float optional new price
        :param amount: float optional new amount
        """
        logger.info(f'Chainflip v.{CONSTANTS.version}: updating limit order - {limit_order.id}')
        if price:
            limit_order.price = price
        if amount:
            limit_order.amount = amount
        await self._api_set_limit_order(limit_order)

        if self._check_for_error_response(function_name='update_limit_order'):
            return
        if self._response:
            try:
                self._order_book.add_limit_order(limit_order)
                logger.info(f'Updated limit order: id={limit_order.id}')
            except Exception as e:
                logger.error(f'update_limit_order: {e}')
        self._log_response()

    async def create_new_range_order(self, range_order: RangeOrder):
        """
        create (mint) a new range order on Chainflip Perseverance.
        :param range_order: RangeOrder type
        """
        logger.info(f'Chainflip v.{CONSTANTS.version}: creating range order - {range_order}')
        await self._api_set_range_order(range_order)

        if self._check_for_error_response(function_name='create_new_range_order'):
            return
        if self._response:
            try:
                self._order_book.add_range_order(range_order)
                logger.info(f'Create new range order: id={range_order.id}')
            except Exception as e:
                logger.error(f'create_range_order: {e}')
        self._log_response()

    async def delete_range_order(self, range_order: RangeOrder):
        """
        delete (burn) a range order on Chainflip Perseverance
        :param range_order: RangeOrder type
        """
        logger.info(f'Chainflip v.{CONSTANTS.version}: deleting range order - {range_order.id}')
        range_order.amount = 0
        range_order.type = CONSTANTS.RangeOrderType.LIQUIDITY
        await self._api_set_range_order(range_order)

        if self._check_for_error_response(function_name='create_new_range_order'):
            return
        if self._response:
            try:
                self._order_book.remove_range_order_by_key(range_order.id)
                logger.info(f'Deleted range order: id={range_order.id}')
            except Exception as e:
                logger.error(f'delete_range_order: {e}')
        self._log_response()

    async def update_range_order(self,
                                 range_order: RangeOrder,
                                 amount: Optional[float] = None,
                                 lower_price: Optional[float] = None,
                                 upper_price: Optional[float] = None):
        """
        update a range order on Chainflip Perseverance
        :param range_order: RangeOrder type
        :param amount: Optional float amount in liquidity
        :param lower_price: Optional float lower price
        :param upper_price: Optional float upper price
        """
        logger.info(f'Chainflip v.{CONSTANTS.version}: update range order - {range_order.id}')
        if amount:
            range_order.amount = amount
        if lower_price and upper_price:
            range_order.lower_price = lower_price
            range_order.upper_price = upper_price

        await self._api_set_range_order(range_order)

        if self._check_for_error_response(function_name='update_range_order'):
            return
        if self._response:
            try:
                self._order_book.add_range_order(range_order)
                logger.info(f'Updated range order: id={range_order.id}')
            except Exception as e:
                logger.error(f'update_range_order: {e}')
        self._log_response()

    async def send_limit_orders(self, limit_orders: list = None):
        """
        send limit order candidates to the Chainflip Perseverance
        :param limit_orders: list of LimitOrder candidates
        :return:
        """
        for order in limit_orders:
            asyncio.create_task(self.create_new_limit_order(order))

    async def send_range_orders(self, range_orders: list = None):
        """
        send range order candidates to the Chainflip Perseverance
        :param range_orders: list of RangeOrder candidates
        :return:
        """
        for order in range_orders:
            asyncio.create_task(self.create_new_range_order(order))

    async def cancel_limit_orders(self, limit_orders: list = None):
        """
        cancel all open limit orders:
        :param limit_orders: list of LimitOrder candidates
        """
        for order in limit_orders:
            asyncio.create_task(self.delete_limit_order(order))

    async def cancel_range_orders(self, range_orders: list = None):
        """
        cancel all range orders
        :param range_orders: list of RangeOrder objects
        """
        for order in range_orders:
            asyncio.create_task(self.delete_range_order(order))
