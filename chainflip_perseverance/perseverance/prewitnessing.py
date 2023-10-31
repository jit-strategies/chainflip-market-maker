import datetime
import asyncio
import websockets
import json

from collections import deque

import chainflip_perseverance.utils.constants as CONSTANTS
import chainflip_perseverance.utils.format as formatter
import chainflip_perseverance.utils.logger as log

from chainflip_perseverance.utils.constants import NetworkStatus
from chainflip_perseverance.utils.data_types import PrewitnessedSwap

logger = log.setup_custom_logger('root')


class PrewitnessedSwaps(object):
    """
    Chainflip prewitnessed swaps object
    """

    def __init__(self, base_asset: str, pair_asset: str = 'Usdc'):
        self._base_asset = formatter.asset_to_str(base_asset)
        self._pair_asset = formatter.asset_to_str(pair_asset)
        if self._base_asset == 'Usdc':
            self._core_asset = self._pair_asset
        else:
            self._core_asset = self._base_asset
        self._block_confirmation_secs = CONSTANTS.BLOCK_TIMINGS[self._core_asset]
        self._block_confirmation_num = CONSTANTS.CHAINFLIP_BLOCK_CONFIRMATIONS[self._core_asset]
        self._end_time = None
        self._swaps = deque(maxlen=200)
        self._swaps_stream = None
        self._stream_connected = NetworkStatus.NOT_CONNECTED

    @property
    def base_asset(self) -> str:
        return self._base_asset

    @property
    def pair_asset(self) -> str:
        return self._pair_asset

    @property
    def swaps(self) -> deque:
        return self._swaps

    @property
    def status(self) -> NetworkStatus:
        return self._stream_connected

    @property
    def block_time(self) -> int:
        return self._block_confirmation_secs

    @property
    def block_number(self) -> int:
        return self._block_confirmation_num

    async def _listen_to_websocket(self, url: str = "ws://localhost:9944"):
        data = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "cf_subscribe_prewitness_swaps",
            "params": [self._base_asset, self._pair_asset]
        }

        async with websockets.connect(url) as websocket:
            await websocket.send(json.dumps(data))
            self._stream_connected = NetworkStatus.CONNECTED

            # Listen for incoming messages
            try:
                await websocket.recv()
                while True:
                    resp = await websocket.recv()
                    resp = json.loads(resp)
                    amount = resp['params']['result'][0] / CONSTANTS.UNIT_CONVERTER[self.base_asset]
                    self._swaps.append(PrewitnessedSwap(
                        base_asset=self.base_asset,
                        pair_asset=self.pair_asset,
                        amount=amount,
                        end_time=datetime.datetime.now() + datetime.timedelta(
                            seconds=self.block_number * self.block_time)
                    ))
                    logger.info(f'Witnessed swap {amount} {self.base_asset} for {self.pair_asset} ')

            except websockets.ConnectionClosed as e:
                logger.error(
                    f'Prewitnessed swaps connection closed {self.base_asset}-{self.pair_asset} {e.code}: {e.reason}'
                )
                self._connected = NetworkStatus.NOT_CONNECTED

            except Exception as e:
                logger.error(f'Prewitnessed swaps stream error occurred {self._base_asset}-{self._pair_asset}: {e}')
                self._connected = NetworkStatus.NOT_CONNECTED

    async def return_swaps(self) -> list:
        block_time = datetime.datetime.now() + datetime.timedelta(seconds=6)
        swaps = []
        while self._swaps and self._swaps[0].end_time <= block_time:
            swaps.append(self._swaps.popleft())
        return swaps

    async def remove_expired_swaps(self):
        now = datetime.datetime.now()
        while self._swaps and self._swaps[-1].end_time <= now:
            self._swaps.pop()

    async def start_websocket(self, url: str = "ws://localhost:9944"):
        self._swaps_stream = asyncio.create_task(self._listen_to_websocket(url))
        await asyncio.sleep(5)
