import asyncio
import random

from web3.auto import Web3

import chainflip_partnernet.utils.logger as log
import chainflip_partnernet.utils.format as formatter
import chainflip_partnernet.utils.settings as settings

from chainflip_partnernet.utils.constants import BLOCK_TIMINGS

from chainflip_partnernet.chainflip_env.swapping_channel import SwappingChannel

logger = log.setup_custom_logger('root')


class MemPoolSim(object):
    """
    Dummy mem pool, not currently used but useful for testing
    """
    def __init__(self, asset: str):
        self._asset = formatter.asset_to_str(asset)
        self._channels = list()
        self._witnessed_deposit = False
        self._timer = BLOCK_TIMINGS[self._asset]

    @property
    def asset(self) -> str:
        return self._asset

    @property
    def channels(self) -> list:
        return self._channels

    @property
    def witnessed(self) -> bool:
        return self._witnessed_deposit

    def add_channel(self, channel: SwappingChannel):
        if channel.is_active:
            if channel.base_asset != self._asset:
                logger.error(f'Unable to add channel to {self._asset} mempool: '
                             f'incorrect channel base asset, should be the same as mempool')
                return
            self._channels.append(channel)
        else:
            logger.error(f'Unable to add channel to {self._asset} mempool: not an active swapping channel')
            pass

    async def witness_deposits(self) -> list:
        await self.sleep()
        deposits = []
        for channel in self._channels:
            if channel.is_active:
                for deposit in channel.deposits:
                    deposits.append(deposit)

        return deposits

    async def sleep(self):
        await asyncio.sleep(self._timer)


class MemPool(object):
    """
    Mempool reader. You will need a chain http address from a provider such as Infura
    """
    def __init__(self, asset: str, wss: str = None):
        """
        Todo: add other assets to mempool checker
        :param asset: [Eth]
        :param wss: web socket address for the chain
        """
        self._asset = formatter.asset_to_str(asset)
        if wss is None:
            wss = settings.infura_http_eth
        self._web3 = Web3(Web3.WebsocketProvider(wss))
        self._is_connected = self._web3.is_connected()
        self._witnessed_deposit = False
        self._filter = 'latest'
        logger.info(f'MemPool active for {asset}')

    @property
    def asset(self) -> str:
        return self._asset

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    @property
    def witnessed(self) -> bool:
        return self._witnessed_deposit

    def submit_addresses_dummy(self, address):
        """
        Randomly assigns a witnessed deposit from the Chainflip partnernet.
        This is a simulator and a demo of how the process will work come mainnet.
        :param address: swapping channel address
        :return:
        """
        amount = random.uniform(0.0, 5)
        self._witnessed_deposit = True
        logger.info(f'{self.asset} Mempool: witnessed deposit for address: {address} with amount: {amount}')

    def _handle_event(self, event):
        try:
            # remove the quotes in the transaction hash
            transaction = Web3.to_json(event).strip('"')
            # use the transaction hash that we removed the '"' from to get the details of the transaction
            transaction = self._web3.eth.get_transaction(transaction)
            logger.info(f'{self.asset} Mempool: witnessed transaction {transaction}')

        except Exception as err:
            # print transactions with errors. Expect to see transactions people submitted with errors
            logger.error(f'{self.asset} Mempool error: {err}')

    async def watch(self, event_filter=None, poll_interval: int = 6):
        if event_filter is None:
            event_filter = self._web3.eth.filter(self._filter)

        logger.info(f'{self.asset} Mempool: Begin watching for transactions')
        while True:
            for event in event_filter.get_new_entries():
                self._handle_event(event)
            await asyncio.sleep(poll_interval)
