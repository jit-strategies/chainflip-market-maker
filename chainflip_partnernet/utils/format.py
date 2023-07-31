import json

from math import log, sqrt

from chainflip_partnernet.utils.constants import ASSETS, UNIT_CONVERTER, DECIMALS


def asset_to_str(asset: str) -> str:
    asset = asset.upper()
    assert(asset in ASSETS.keys())
    return ASSETS[asset]


def asset_to_amount(asset: str, amount: float) -> int:
    if asset not in ASSETS.values():
        asset = asset_to_str(asset)

    amount = UNIT_CONVERTER[asset] * amount
    return int(amount)


def calculate_sqrt_price(price: float, asset_1: str, asset_2: str = 'Usdc') -> int:
    precision = DECIMALS[asset_1] + DECIMALS[asset_2]
    return int(str(round(sqrt(price) * pow(2, 96)))[:precision+1])


def calculate_price_from_sqrt_price(sqrt_price_x_96: int, asset_1: str, asset_2: str = 'Usdc') -> float:
    price = (sqrt_price_x_96 / pow(2, 96)) ** 2 * (UNIT_CONVERTER[asset_1] / UNIT_CONVERTER[asset_2])
    return price


def price_to_tick(asset: str, price: float) -> int:
    if asset not in ASSETS.values():
        asset = asset_to_str(asset)

    sqrt_price_x_96 = calculate_sqrt_price(price, asset)
    return 2 * round(log(sqrt_price_x_96 / 2 ** 96) / log(1.0001))


def tick_to_price(tick: int, asset_1: str, asset_2: str = 'Usdc') -> float:
    if asset_1 not in ASSETS.values():
        asset_1 = asset_to_str(asset_1)
    if asset_2 not in ASSETS.values():
        asset_2 = asset_to_str(asset_2)
    price = 1.0001 ** tick
    return price * (UNIT_CONVERTER[asset_1] / UNIT_CONVERTER[asset_2])


def deserialize_balance(response: dict) -> dict:
    return json.loads(response['result'])
