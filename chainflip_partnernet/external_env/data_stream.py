import asyncio
from datetime import datetime
from binance import AsyncClient, BinanceSocketManager

import chainflip_partnernet.utils.logger as log

from chainflip_partnernet.utils.data_types import BinanceKline


logger = log.setup_custom_logger('root')


class BinanceDataFeed:
    """
    Data stream object for Binance. This could be easily changes to another provider
    """
    def __init__(self):
        self._name = None
        self._interval = None
        self._client = None
        self._manager = None
        self._socket = None
        self._data = None
        self._intervals = {
            '1m': 30,
            '30s': 30
        }

    def __str__(self):
        return f'BinanceDataFeed: {self._name}'

    @property
    def name(self):
        return self._name

    @property
    def interval(self):
        return self._interval

    @property
    def data(self):
        return self._data

    def create_new(self, interval: str = '1m', asset: str = 'ETHUSDC'):
        """
        create new data feed with interval on asset
        :param interval: interval string, must match a key in self._intervals dict
        :param asset: known asset on the data feed
        :return:
        """
        self._name = asset
        self._interval = interval

    async def __call__(self):
        """
        activates the data feed. Takes the response and parses it into a Kline object for Binance
        :return:
        """
        self._client = await AsyncClient.create()
        self._manager = BinanceSocketManager(self._client)
        self._socket = self._manager.kline_socket(self._name, self._interval)
        logger.info(f'Created new binance socket for klines with {self._interval} interval: {self} ')
        async with self._socket as socket:
            while True:
                res = await socket.recv()
                try:
                    self._data = BinanceKline(
                        start_time=datetime.fromtimestamp(res['k']['t'] / 1000),
                        end_time=datetime.fromtimestamp(res['k']['T'] / 1000),
                        ticker=res['k']['s'],
                        interval=res['k']['i'],
                        open=float(res['k']['o']),
                        close=float(res['k']['c']),
                        high=float(res['k']['h']),
                        low=float(res['k']['l']),
                        volume=float(res['k']['v']),
                    )
                    logger.info(f'Received Binance candle: {self._data}')
                except Exception as e:
                    logger.error(f'Error in getting Binance data point: {e}')

                await self.sleep()


        await client.close_connection()

    async def sleep(self):
        interval = self._intervals[self._interval]
        await asyncio.sleep(interval)
