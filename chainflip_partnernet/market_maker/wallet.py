import os
import asyncio

from typing import Union
from dotenv import load_dotenv
from web3 import Web3

import chainflip_partnernet.utils.logger as log
import chainflip_partnernet.utils.constants as CONSTANTS

from chainflip_partnernet.utils.token import ERC20Token


logger = log.setup_custom_logger('root')


class InfuraWalletHandler:
    """
    Wallet handler class. Works best with Metamask but any wallet should work.
    """
    def __init__(self, infura_http: str):
        """
        to use this you need to add your http address in settings and your wallet private key in a .env file
        :param infura_http: current infura http address
        """
        load_dotenv()
        self._web3 = Web3(Web3.HTTPProvider(infura_http))
        self._eth_wallet_private_key = os.getenv('ETH_WALLET_PRIVATE_KEY')
        self._btc_wallet_private_key = None
        try:
            self._eth_wallet = self._web3.eth.account.from_key(self._eth_wallet_private_key)
            self._btc_wallet = None
        except Exception as e:
            logger.info(f'Failed to initialise wallets - {e}')
            raise
        self._is_connected = True
        self._eth_balance = 0
        self._btc_balance = 0
        self._latest_eth_tx = None
        self._latest_btc_tx = None
        self._tokens = {}
        self._addresses = {}
        logger.info(f'Initialised wallet handler for market maker - _is_connected = {self._is_connected}')

    @property
    def web3_connection(self) -> Web3:
        return self._web3

    @property
    def eth_wallet(self):
        return self._eth_wallet

    @property
    def btc_wallet(self):
        return self._btc_wallet

    @property
    def is_connected(self) -> bool:
        return self._web3.is_connected()

    @property
    def balance(self) -> Union[int, float]:
        return self._eth_balance

    @property
    def address(self) -> dict:
        return self._addresses

    def _get_address(self, asset: str) -> str:
        """
        returns address for an asset
        :param asset: [Eth, Usdc]
        :return: str address
        """
        return self._addresses[asset]

    def _get_nonce_for_eth_account(self):
        """
        get a nonce for the current Eth account
        :return: nonce object
        """
        nonce = self._web3.eth.get_transaction_count(self._eth_wallet.address)
        logger.info(f'Acquired nonce for wallet {self._eth_wallet.address} - nonce number: {nonce}')
        return nonce

    async def _check_transaction(self, tx):
        """
        check transaction on the Eth chain and logs outcome
        :param tx: transaction hash object
        :return:
        """
        live = True
        transaction = None
        while live:
            try:
                transaction = self._web3.eth.get_transaction(tx)
            except Exception as e:
                logger.error(f'Check transaction error: {e} - waiting 6 seconds')
                await asyncio.sleep(6)
            break

        assert transaction["from"] == self._eth_wallet.address
        self._latest_eth_tx = transaction
        logger.info(f'Last transaction for wallet - {self._latest_eth_tx}')

    def add_address_manually(self, address: str, asset: str):
        """
        manually add the address to an asset
        :param address: string object
        :param asset: [Eth, Usdc]
        :return:
        """
        self._addresses[asset] = address

    def get_eth_balance_in_eth(self):
        """
        get current Eth balance from wallet
        :return: float balance
        """
        self._eth_balance = self._web3.eth.get_balance(account=self._eth_wallet.address)
        return self._web3.from_wei(self._eth_balance, unit='ether')

    def get_eth_balance_in_gwei(self):
        """
        get current Eth balance in Gwei
        :return: float balance
        """
        self._eth_balance = self._web3.eth.get_balance(account=self._eth_wallet.address)
        return self._web3.from_wei(self._eth_balance, unit='gwei')

    def add_token(self, token: str, contract_address: str):
        """
        add token to the list of tokens the wallet can use
        :param token: [Eth, Usdc]
        :param contract_address: contract address
        :return:
        """
        self._tokens.update(
            [(token, ERC20Token(name=token, address=self._web3.to_checksum_address(contract_address)))]
        )

    def see_token_total_supply(self, token: str):
        """
        return total token supply from the chain
        :param token: [Eth, Usdc]
        :return:
        """
        return self._tokens[token](self._web3).functions.totalSupply().call()

    async def transfer_eth_to_account(

            self,
            amount_in_eth: float,
            address: str = None,
            gas: int = None,
            gas_price: int = None
    ):
        """
        transfer Eth from wallet to an account, logs response
        :param amount_in_eth: float amount to transfer
        :param address: address to transfer to
        :param gas: gas you wish to pay, if None value is imported from CONSTANTS
        :param gas_price: current gas price, if None value is imported from CONSTANTS
        :return:
        """
        if gas is None:
            gas = self._web3.to_wei(CONSTANTS.GAS, unit='gwei')
        if gas_price is None:
            gas_price = CONSTANTS.GAS_PRICE

        assert self._is_connected is True, logger.info(f'Wallet has disconnected')
        if address is None:
            address = self._get_address(asset='Eth')
        else:
            self._addresses['Eth'] = address

        tx_hash = {
            'nonce': self._get_nonce_for_eth_account(),
            'from': self._eth_wallet.address,
            'to': self._web3.to_checksum_address(address),
            'value': self._web3.to_wei(amount_in_eth, unit='ether'),
            'gas': gas,
            'gasPrice': gas_price
        }
        signed_tx = self._web3.eth.account.sign_transaction(tx_hash, self._eth_wallet_private_key)
        try:
            tx = self._web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        except Exception as e:
            logger.error(f'Failed to send Eth transaction: {e} - check gas price')
            return
        logger.info(f'Sent Eth transaction for wallet {self._eth_wallet.address} with transaction hash: {tx_hash}')
        await self._check_transaction(tx)

    async def transfer_dai_to_account(
            self,
            amount_in_dai: int,
            address: str = None,
            gas: int = None,
            gas_price: int = None
    ):
        """
        transfer Dai from wallet to an account, logs response
        :param amount_in_dai: float amount to transfer
        :param address: address to transfer to
        :param gas: gas you wish to pay, if None value is imported from CONSTANTS
        :param gas_price: current gas price, if None value is imported from CONSTANTS
        :return:
        """
        assert 'Dai' in self._tokens.keys(), \
                logger.error(f'Dai not in initialised tokens, initialise it first with '
                             f'add_token(other, contract_address="..."')
        if gas is None:
            gas = self._web3.to_wei(CONSTANTS.GAS, unit='gwei')
        if gas_price is None:
            gas_price = CONSTANTS.GAS_PRICE

        assert self._is_connected is True, logger.info(f'Wallet has disconnected')
        if address is None:
            address = self._get_address(asset='Dai')
        else:
            self._addresses['Dai'] = address

        tx_hash = self._tokens['dai'](self._web3).functions.transfer(
            self._web3.to_checksum_address(address), self._web3.to_hex(amount_in_dai)
        ).buildTransaction({
            'nonce': self._get_nonce_for_eth_account(),
            'gas': gas,
            'gasPrice': gas_price
        })
        signed_tx = self._web3.eth.account.sign_transaction(tx_hash, self._eth_wallet_private_key)
        try:
            tx = self._web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        except Exception as e:
            logger.error(f'Failed to send Dai transaction: {e} - check gas price')
            return
        logger.info(f'Sent Dai transaction for wallet {self._eth_wallet.address} with transaction hash: {tx_hash}')
        await self._check_transaction(tx)

    async def transfer_usdc_to_account(
            self,
            amount_in_usdc: int,
            address: str = None,
            gas: int = None,
            gas_price: int = None
    ):
        """
        transfer Dai from wallet to an account, logs response
        :param amount_in_usdc: amount to transfer
        :param address: address to transfer to
        :param gas: gas you wish to pay, if None value is imported from CONSTANTS
        :param gas_price: current gas price, if None value is imported from CONSTANTS
        :return:
        """
        assert 'Usdc' in self._tokens.keys(), \
                logger.error(f'Usdc not in initialised tokens, initialise it first with '
                             f'add_token(other, contract_address="..."')
        if gas is None:
            gas = self._web3.to_wei(CONSTANTS.GAS, unit='gwei')
        if gas_price is None:
            gas_price = CONSTANTS.GAS_PRICE

        assert self._is_connected is True, logger.info(f'Wallet has disconnected')
        if address is None:
            address = self._get_address(asset='Usdc')
        else:
            self._addresses['Usdc'] = address

        try:
            tx_hash = self._tokens['Usdc'](self._web3).functions.transfer(
                self._web3.to_checksum_address(address), self._web3.to_hex(amount_in_usdc)
            ).buildTransaction({
                'nonce': self._get_nonce_for_eth_account(),
                'gas': gas,
                'gasPrice': gas_price
            })
            signed_tx = self._web3.eth.account.sign_transaction(tx_hash, self._eth_wallet_private_key)
        except Exception as e:
            logger.error(f'Failed to build tx hash and sign it: {e}')
            return
        try:
            tx = self._web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        except Exception as e:
            logger.error(f'Failed to send Usdc transaction: {e} - check gas price')
            return
        logger.info(f'Sent Usdc transaction for wallet {self._eth_wallet.address} with transaction hash: {tx_hash}')
        await self._check_transaction(tx)
