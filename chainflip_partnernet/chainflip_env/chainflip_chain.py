import asyncio
import random
from typing import Union

import chainflip_partnernet.utils.logger as log

from chainflip_partnernet.chainflip_env.chainflip_amm import Amm
from chainflip_partnernet.chainflip_env.swapping_channel import SwappingChannel
from chainflip_partnernet.external_env.mem_pools import MemPool, MemPoolSim

logger = log.setup_custom_logger('root')


class ChainflipChain(object):
    """
    Dummy Chainflip Chain demonstrating how the mainnet chain will communicate with LP systems.
    This is just a simulator.
    Todo: Remove at mainnet when replaced with true Chainflip Chain
    """
    def __init__(self, strategy: str = 'stream'):
        self._strategy = strategy
        self._swaps = list()
        self._swapping_channels = dict()
        self._mem_pools = list()
        self._amm = Amm()
        self._current_key = 0
        self._timer = 6

    @property
    def swaps(self) -> list:
        return self._swaps

    @property
    def channels(self) -> dict:
        return self._swapping_channels

    @property
    def mem_pools(self) -> list:
        return self._mem_pools

    @property
    def amm(self) -> Amm:
        return self._amm

    def add_channel(self, channel: SwappingChannel = None):
        if channel is None:
            channel = SwappingChannel.generate_new()
        if channel.is_active:
            self._swapping_channels.update([(self._current_key, channel)])
            self._current_key += 1
            logger.info(f'Added swapping channel to chainflip state chain: {channel}')
        else:
            logger.error(
                'Unable to add channel to Chainflip chain: not an active swapping channel'
            )
            pass

    def close_channels(self):
        if len(self._swapping_channels) == 0:
            return
        else:
            self._swapping_channels.clear()

    def add_mem_pool(self, mem_pool: Union[MemPool, MemPoolSim]):
        self._mem_pools.append(mem_pool)

    def add_swaps(self):
        for mem_pool in self._mem_pools:
            swaps = mem_pool.witness_deposits()
            for swap in swaps:
                self.swaps.append(swap)

    def send_swapping_channels(self):
        return self.channels

    async def execute_swaps(self):
        await self.sleep()
        self._amm.add_swaps(self._swaps)
        self._amm.begin_matching_1()
        self._swaps.clear()

    async def sleep(self):
        await asyncio.sleep(self._timer)

    async def run(self):
        while True:
            random_num = random.randint(0, 5)
            if self._strategy == 'stream':
                await self.execute_swaps()
            else:
                if random_num == 0:
                    self.add_channel()
                    await self.execute_swaps()
                elif random_num in [1, 3]:
                    await self.execute_swaps()
                elif random_num == 4:
                    self.close_channels()
                    await self.execute_swaps()
                elif random_num == 5:
                    try:
                        self._mem_pools[0].submit_addresses_dummy(self._swapping_channels[0])
                    except KeyError:
                        self._mem_pools[0].submit_addresses_dummy(SwappingChannel.generate_new())
                        await self.execute_swaps()
