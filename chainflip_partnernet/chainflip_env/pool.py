import random

import chainflip_partnernet.utils.logger as log

from chainflip_partnernet.external_env.data_stream import BinanceDataFeed


logger = log.setup_custom_logger('root')


class Pool(object):
    """
    Dummy pool object. Has no liquidity in it, but simply tracks prices to simulate a real pool for info to LP systems
    """
    def __init__(self, feed: BinanceDataFeed, asset: str = 'ETHUSDC'):
        self._feed = feed
        self._asset = asset
        self._pool_price = 0.

    @property
    def asset(self):
        return self._asset

    @property
    def pool_price(self):
        self.set_price()
        return self._pool_price

    def set_price(self):
        """
        Sets a random price within a range based on current prices
        :return:
        """
        try:
            current_price = self._feed.data.close
            deviation = random.uniform(-0.2, 0.2)
            self._pool_price = current_price + deviation
        except:
            self._pool_price = None

    def get_current_price(self):
        logger.info(f'Current pool price: {self.pool_price}')
