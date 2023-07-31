from datetime import datetime
from typing import Union

import chainflip_partnernet.utils.logger as log
import chainflip_partnernet.utils.constants as CONSTANTS
import chainflip_partnernet.utils.format as formatter
import chainflip_partnernet.utils.settings as settings

from chainflip_partnernet.utils.constants import CommandMap as Flip
from chainflip_partnernet.utils.data_types import LimitOrder, RangeOrder

from chainflip_partnernet.chainflip_env.chainflip_chain import ChainflipChain
from chainflip_partnernet.chainflip_env.commands import SendCommand
from chainflip_partnernet.market_maker.wallet import InfuraWalletHandler
from chainflip_partnernet.market_maker.book import Book


logger = log.setup_custom_logger('root')


class MarketMaker:
    """
    Market maker class handler.
    Many features which are desirable are not included.
    """
    def __init__(self, chainflip: ChainflipChain, market_maker_id: str):
        """
        :param chainflip: Dummy Chainflip Chain
        :param market_maker_id: The id used for sending commands to the Chainflip partnernet
        """
        self._chainflip = chainflip
        self._wallet = InfuraWalletHandler(settings.infura_http_eth)
        self._id = market_maker_id
        self._commands = SendCommand(self._id)
        self._order_book = Book()
        self._response = None
        self._order_key = 0
        logger.info(f'Initialised Market Maker with id: {self._id}')

    @property
    def response(self) -> str:
        return self._response

    @property
    def wallet(self):
        return self._wallet

    @property
    def open_limit_orders(self) -> dict:
        return self._order_book.limit_orders

    @property
    def open_range_orders(self) -> dict:
        return self._order_book.range_orders

    @property
    def book_balance(self) -> dict:
        return self._order_book.balance

    def check_wallet_balances(self):
        """
        check current wallet balances from internal wallet
        """
        balance = self._wallet.get_eth_balance_in_eth()
        logger.info(f'Current Eth balance for address {self._wallet.eth_wallet.address} = {balance} Eth')

    def register_token_for_wallet(self, token: str):
        """
        to move money from the internal wallet a token needs to be registered with its contract address
        :param token: [Eth, Dot, Btc, Usdc, Flip]
        :return:
        """
        token = formatter.asset_to_str(token)
        assert (token in CONSTANTS.TOKEN_CONTRACT_ADDRESS.keys()), f'{token} not currently supported'
        self._wallet.add_token(token, contract_address=CONSTANTS.TOKEN_CONTRACT_ADDRESS[token])
        logger.info(f'Added token {token} to Wallet, can now send this token')

    def log_response(self):
        """
        logs the response from Chainflip partnernet
        :return:
        """
        logger.info(f'Chainflip v.{CONSTANTS.version} response:{self._response["result"]}')

    def check_log_error(self, function_name: str) -> bool:
        """
        check for an error from the Chainflip partnernet and log it
        :param function_name: str for where the call originated from
        :return: boolean
        """
        if 'error' in self._response:
            logger.error(f'{function_name}: {self._response["error"]["message"]}')
            return True
        else:
            return False

    def register(self):
        """
        register LP account on the Chainflip partnernet
        :return:
        """
        logger.info(f'Chainflip v.{CONSTANTS.version}: register provider')
        self._response = self._commands(Flip.Register)
        self.log_response()

    async def get_asset_balances(self):
        """
        get current LP balances on the Chainflip partnernet, updates balances and logs response
        :return:
        """
        logger.info(f'Chainflip v.{CONSTANTS.version}: asset balances')
        self._response = await self._commands(Flip.AssetBalances)
        if self.check_log_error(function_name='get_asset_balances'):
            return
        self._order_book.update_balance(formatter.deserialize_balance(self._response))
        logger.info(f'Current asset balances: {self.book_balance}')

    async def deposit_asset(self, amount: Union[float, int], asset: str):
        """
        Todo: Add other assets to deposit
        deposit asset from internal wallet to Chainflip partnernet
        :param amount: amount of asset to deposit
        :param asset: [Eth, Usdc]
        :return:
        """
        asset = formatter.asset_to_str(asset)
        if asset == 'Eth':
            await self._wallet.transfer_eth_to_account(amount)
        elif asset == 'Usdc':
            await self._wallet.transfer_usdc_to_account(amount)

    async def withdraw_asset(self, amount: Union[float, int], asset: str):
        """
        withdraw asset from current Chainflip partnernet
        :param amount: amount you wish to withdraw
        :param asset: [Eth, Dot, Btc, Usdc, Flip]
        :return:
        """
        self._response = self._commands(
            Flip.WithdrawAsset,
            amount, asset, self._wallet.eth_wallet.address
        )

    async def open_liquidity_deposit(self, amount: float, asset: str):
        """
        open a liquidity deposit address for the Chainflip partnernet. This must be done before depositing liquidity.
        An address will be returned by Chainflip partnernet and internal wallet will deposit
        :param amount: amount to deposit
        :param asset: [Eth, Dot, Btc, Usdc, Flip]
        :return:
        """
        asset = formatter.asset_to_str(asset)
        logger.info(f'Chainflip v.{CONSTANTS.version}: open {asset} liquidity deposit')
        self._response = await self._commands(Flip.LiquidityDeposit, asset)
        if self.check_log_error(function_name='open_liquidity_deposit'):
            return
        self.log_response()
        address = self._response.text.split('"')[7]
        logger.info(f'Sending {amount} {asset} to {address}')
        if asset == 'Eth':
            await self._wallet.transfer_eth_to_account(amount_in_eth=amount, address=address)
        elif asset == 'Usdc':
            amount = round(CONSTANTS.UNIT_CONVERTER[asset] * amount)
            await self._wallet.transfer_usdc_to_account(amount_in_usdc=amount, address=address)

    async def mint_limit_order(self, limit_order: LimitOrder):
        """
        mint a limit order on Chainflip partnernet
        :param limit_order: LimitOrder type
        :return:
        """
        logger.info(f'Chainflip v.{CONSTANTS.version}: minting limit order - {limit_order}')
        self._response = await self._commands(
            Flip.MintLimitOrder,
            limit_order.amount, limit_order.asset, limit_order.price, limit_order.side
        )
        if self.check_log_error(function_name='mint_limit_order'):
            return
        if self._response:
            self._order_book.add_limit_order(limit_order)
            logger.info(f'Minted limit order')
        self.log_response()

    async def burn_limit_order(self, timestamp: datetime = None, limit_order: LimitOrder = None):
        """
        burn a limit order on Chainflip partnernet by timestamp
        if no timestamp is given, the latest order is burnt
        :param timestamp: optional Datetime object
        :param limit_order: optional LimitOrder object
        :return:
        """
        if limit_order is None:
            try:
                limit_order = self._order_book.get_limit_order_by_timestamp(timestamp)
            except KeyError:
                logger.info(f'{"burn_limit_order"} - No limit order open')
                return

        logger.info(f'Chainflip v.{CONSTANTS.version}: burning limit order - {limit_order}')
        self._response = await self._commands(
            Flip.BurnLimitOrder,
            limit_order.amount, limit_order.asset, limit_order.price, limit_order.side
        )
        if self.check_log_error(function_name='burn_limit_order'):
            return
        if self._response:
            self._order_book.remove_limit_order_by_timestamp(timestamp)
            logger.info(f'Burnt limit order')
        self.log_response()

    async def mint_range_order(self, range_order: RangeOrder):
        """
        mint range order on Chainflip partnernet
        there are two ways to do this, by exact PoolLiquidity or by AssetAmounts

        PoolLiquidity - submit an amount which is supplied into the pool across the range given
                    (this amount is not exact due to tick spacings)

        AssetAmounts - attempts to mint an order up to the desired amount set but will not mint less than the minimum
                       amount. stable always refers to Usdc, unstable is the other currency
        {"AssetAmounts":{"desired":{"unstable":10, "stable":0}, "minimum":{"unstable":8, "stable":0}}

        :param range_order: RangeOrder type
        :return:
        """
        logger.info(f'Chainflip v.{CONSTANTS.version}: minting range order - {range_order}')
        if range_order.type == CONSTANTS.RangeOrderType.LIQUIDITY:
            self._response = await self._commands(
                Flip.MintRangeOrderLiquidity,
                range_order.amount, range_order.asset, range_order.lower_price, range_order.upper_price
            )
        elif range_order.type == CONSTANTS.RangeOrderType.ASSET_AMOUNTS_STABLE:
            self._response = await self._commands(
                Flip.MintRangeOrderAssetAmounts,
                range_order.amount,
                range_order.asset,
                range_order.lower_price,
                range_order.upper_price,
                range_order.minimum_amount,
                False
            )
        elif range_order.type == CONSTANTS.RangeOrderType.ASSET_AMOUNTS_UNSTABLE:
            self._response = await self._commands(
                Flip.MintRangeOrderAssetAmounts,
                range_order.amount,
                range_order.asset,
                range_order.lower_price,
                range_order.upper_price,
                range_order.minimum_amount,
                True
            )
        else:
            logger.error(f'mint_range_order: Unsupported type of range order submitted - {range_order.type}')

        if self.check_log_error(function_name='mint_range_order'):
            return
        if self._response:
            self._order_book.add_range_order(range_order)
            logger.info(f'Minted range order')
        self.log_response()

    async def burn_range_order(self, timestamp: datetime = None, range_order: RangeOrder = None):
        """
        burn a range order on the Chainflip partnernet by timestamp
        if no timestamp is given the latest order is burnt
        :param timestamp: Datetime object
        :return:
        """
        if range_order is None:
            try:
                range_order = self._order_book.get_range_order_by_timestamp(timestamp)
            except KeyError:
                logger.info(f'{"burn_range_order"} - No range order open')
                return

        logger.info(f'Chainflip v.{CONSTANTS.version}: burning range order - {range_order}')
        self._response = await self._commands(
            Flip.BurnRangeOrder,
            range_order.amount, range_order.asset, range_order.lower_price, range_order.upper_price
        )
        if self.check_log_error(function_name='burn_range_order'):
            return
        if self._response:
            self._order_book.remove_range_order_by_timestamp(timestamp)
            logger.info(f'Burnt range order')
        self.log_response()

    async def send_limit_orders(self, limit_orders: list = None):
        """
        send limit order candidates to the Chainflip partnernet
        :param limit_orders: list of limit order candidates
        :return:
        """
        for order in limit_orders:
            await self.mint_limit_order(order)

    async def send_range_orders(self, range_orders: list = None):
        """
        send range order candidates to the Chainflip partnernet
        :param range_orders: list of range order candidates
        :return:
        """
        for order in range_orders:
            await self.mint_range_order(order)

    async def burn_all_limit_orders(self):
        for order in self._order_book.limit_orders:
            await self.burn_limit_order(order)

    async def burn_all_range_order(self):
        for order in self._order_book.range_orders:
            await self.burn_range_order(order)
