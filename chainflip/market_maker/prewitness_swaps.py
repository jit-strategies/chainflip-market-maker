
import chainflip.utils.format as formatter
import chainflip.utils.logger as log

from chainflip.exchange.prewitnessing import PrewitnessedSwaps


logger = log.setup_custom_logger('root')


class Prewitnesser:
    def __init__(self, user_id: str):
        self._id = user_id
        self._prewitnesser = dict()

    async def add_prewitness_stream(self, base_asset, pair_asset):
        stream = PrewitnessedSwaps(formatter.asset_to_str(base_asset), formatter.asset_to_str(pair_asset))
        self._prewitnesser[f'{base_asset}-{pair_asset}'] = stream
        await stream.start_websocket()

    async def get_connection_status(self):
        for key in self._prewitnesser.keys():
            status = self._prewitnesser[key].status
            logger.info(f'Stream status for {key} - {status}')

    async def get_swaps(self, base_asset: str, pair_asset: str) -> list:
        try:
            return await self._prewitnesser[f'{base_asset}-{pair_asset}'].return_swaps()
        except KeyError:
            logger.error(f"get_swaps: Prewitnesser not active for {base_asset}-{pair_asset}")
