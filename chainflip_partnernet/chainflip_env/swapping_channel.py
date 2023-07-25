
from datetime import timedelta, datetime

import chainflip_partnernet.utils.logger as log
import chainflip_partnernet.utils.format as formatter

from chainflip_partnernet.utils.data_types import Swap
from chainflip_partnernet.utils.eth_address import get_new_address


logger = log.setup_custom_logger('root')


class SwappingChannel(object):
    """
    Dummy swapping channel object that operates as a Chainflip swapping channel.
    Todo: Remove come mainnet
    """
    def __init__(self, base_asset: str, quote_asset: str, key: str, expiry: timedelta = timedelta(seconds=1000)):
        self._base_asset = formatter.asset_to_str(base_asset)
        self._quote_asset = formatter.asset_to_str(quote_asset)
        self._key = key
        self._expiry = expiry
        self._is_active = True
        self._start = datetime.now()
        self._end = self._start + self._expiry
        self._deposits = list()

    def __str__(self):
        return f'Base asset: {self.base_asset}, destination asset: {self.quote_asset}, key: {self.key}. ' \
               f'Will expire at {self._expiry}'

    @property
    def base_asset(self) -> str:
        return self._base_asset

    @property
    def quote_asset(self) -> str:
        return self._quote_asset

    @property
    def key(self) -> str:
        return self._key

    @property
    def expiry(self) -> datetime:
        return self._end

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def deposits(self) -> list:
        return self._deposits

    def check(self):
        if datetime.now() > self._end:
            self._is_active = False

    def make_deposit(self, amount):
        assert(amount >= 0)
        self._deposits.append(
            Swap(base_asset=self._base_asset, destination_asset=self._quote_asset, amount=amount, key=self._key)
        )

    @staticmethod
    def generate_new():
        return SwappingChannel(base_asset='Usdc', quote_asset='Eth', key=get_new_address())
