import chainflip_perseverance.utils.format as formatter


class SwappingChannel(object):
    def __init__(self, base_asset: str, quote_asset: str, address: str):
        self._base_asset = formatter.asset_to_str(base_asset)
        self._quote_asset = formatter.asset_to_str(quote_asset)
        self._address = address

    def __str__(self):
        return f'Base asset: {self._base_asset}, Quote asset: {self._quote_asset}, Address: {self._address}'

    @property
    def base_asset(self) -> str:
        return self._base_asset

    @property
    def quote_asset(self) -> str:
        return self._quote_asset

    @property
    def address(self) -> str:
        return self._address
