import asyncio
import websockets
import json

import chainflip.utils.logger as log

from chainflip.utils.constants import NetworkStatus


logger = log.setup_custom_logger('root')


class ChainflipUpdates(object):
    """
    Chainflip updates stream
    """

    def __init__(self, lp_account: str):
        self._lp_id = lp_account
        self._update_stream = None
        self._confirmed_block_number = 0
        self._latest_block_number = 0
        self._stream_connected = NetworkStatus.NOT_CONNECTED

    @property
    def confirmed_block_number(self) -> int:
        return self._confirmed_block_number

    @property
    def latest_block_number(self) -> int:
        return self._latest_block_number

    @confirmed_block_number.setter
    def confirmed_block_number(self, block: int):
        self._confirmed_block_number = block
        self._latest_block_number = block + 2

    async def _listen_to_websocket(self, url: str = 'ws://localhost:10589'):
        data = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "lp_subscribe_order_fills",
            "params": []
        }

        async with websockets.connect(url) as websocket:
            await websocket.send(json.dumps(data))
            self._stream_connected = NetworkStatus.CONNECTED

            # Listen for incoming messages
            try:
                await websocket.recv()
                while True:
                    response = await websocket.recv()
                    response = json.loads(response)
                    await self._process_websocket_message(response['params']['result'])

            except websockets.ConnectionClosed as e:
                logger.error(
                    f'Updates stream connection closed {e.code}: {e.reason}'
                )
                self._connected = NetworkStatus.NOT_CONNECTED

            except Exception as e:
                logger.error(f'Updates stream stream error occurred: {e}')
                self._connected = NetworkStatus.NOT_CONNECTED

    async def _process_websocket_message(self, response: dict):
        """
        This is where processing of fills occurs
        Add whatever logic you wish here, in this demo we just report a fill without doing anything about it
        """
        self.confirmed_block_number = response['block_number']
        order_fills = list()
        for order in response['fills']:
            if 'limit_order' in order:
                limit_order_fill = order['limit_order']
                if limit_order_fill['lp'] == self._lp_id:
                    # add logic here if needed
                    order_fills.append(order)

            if 'range_order' in order:
                limit_order_fill = order['range_order']
                if limit_order_fill['lp'] == self._lp_id:
                    # add logic here if needed
                    order_fills.append(order)

        logger.info(f'Confirmed Chainflip Block: {self._confirmed_block_number}. Latest Block: {self._latest_block_number}')
        logger.info(f'Number of fills in last block: {len(order_fills)}')

    async def start_websocket(self, url: str = 'ws://localhost:10589'):
        self._update_stream = asyncio.create_task(self._listen_to_websocket(url))
        logger.info('Connected to Chainflip updates stream')
        await asyncio.sleep(1)
