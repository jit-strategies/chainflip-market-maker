import asyncio
import json
import websockets

import chainflip.utils.format as formatter
import chainflip.utils.logger as log

from chainflip.utils.constants import NetworkStatus

logger = log.setup_custom_logger('root')


class Pool(object):
    """
    Chainflip Pool object
    """

    def __init__(self, base_asset: str, quote_asset: str = 'USDC'):
        self._base_asset = formatter.asset_to_str(base_asset)
        self._quote_asset = formatter.asset_to_str(quote_asset)
        self._current_price = None
        self._pool_fees = None
        self._pool_liquidity = None
        self._pool_orders = None
        self._price_stream = None
        self._stream_connected = NetworkStatus.NOT_CONNECTED

    def __str__(self):
        if self._pool_fees is None:
            return f'{self._base_asset}-{self._quote_asset}'
        return f'{self._base_asset}-{self._quote_asset}: {self._pool_fees}'

    @property
    def base_asset(self) -> str:
        return self._base_asset

    @property
    def quote_asset(self) -> str:
        return self._quote_asset

    @property
    def price(self) -> float:
        return self._current_price

    @property
    def fees(self) -> dict:
        return self._pool_fees

    @property
    def liquidity(self) -> dict:
        return self._pool_liquidity

    @property
    def orders(self) -> dict:
        return self._pool_orders

    @property
    def connection_status(self) -> NetworkStatus:
        return self._stream_connected

    @fees.setter
    def fees(self, fees: dict):
        self._pool_fees = fees

    @liquidity.setter
    def liquidity(self, liquidity: dict):
        self._pool_liquidity = liquidity

    @orders.setter
    def orders(self, orders: dict):
        self._pool_orders = orders

    async def _listen_to_websocket(self, user_id: str, url: str = "ws://localhost:9944"):
        data = {
            "id": user_id,
            "jsonrpc": "2.0",
            "method": "cf_subscribe_pool_price",
            "params": [self._base_asset, self._quote_asset]
        }

        async with websockets.connect(url) as websocket:
            await websocket.send(json.dumps(data))
            self._stream_connected = NetworkStatus.CONNECTED

            # Discard the first element from the subscription
            await websocket.recv()

            # Listen for incoming messages
            try:
                while True:
                    resp = await websocket.recv()
                    resp = json.loads(resp)
                    self._current_price = formatter.hex_price_to_decimal(
                        resp['params']['result']['price'],
                        self._base_asset,
                        self._quote_asset
                    )
                    logger.info(f'{self._base_asset}-{self._quote_asset} pool price: {self.price}')

            except websockets.ConnectionClosed as e:
                logger.error(f'Pool price connection closed {self._base_asset}-{self._quote_asset} {e.code}: {e.reason}')
                self._connected = NetworkStatus.NOT_CONNECTED

            except Exception as e:
                logger.error(f'Pool price stream error occurred {self._base_asset}-{self._quote_asset}: {e}')
                self._connected = NetworkStatus.NOT_CONNECTED

    async def start_websocket(self, user_id: str, url: str = "ws://localhost:9944"):
        self._price_stream = asyncio.create_task(self._listen_to_websocket(user_id=user_id, url=url))
        logger.info(f'Subscribed to pool price stream for pool: {self.base_asset}-{self.quote_asset}')
        await asyncio.sleep(10)
