from math import log, floor

from chainflip.utils.constants import ASSETS, UNIT_CONVERTER, DECIMALS


def asset_to_str(asset: str) -> str:
    """
    convert an asset str to the correct format, e.g. Eth, Btc ...
    :param asset: str for the asset
    :return
    """
    asset = asset.upper()
    assert(asset in ASSETS.keys())
    return ASSETS[asset]


def amount_in_asset(asset: str, amount: float) -> int:
    """
    convert the amount given to an amount in the base of the given asset. E.g. convert Eth to Wei
    :param asset: str for the asset
    :param amount: float amount for the asset
    :return: integer amount for the converted amount
    """
    amount = UNIT_CONVERTER[asset] * amount
    return int(amount)


def calculate_sqrt_price(price: float, asset_1: str, asset_2: str = 'USDC') -> int:
    """
    calculate the sqrt price for a base asset in terms of a pair asset
    :param price: float amount of asset 1 in asset 2
    :param asset_1: str for the base asset
    :param asset_2: str for the pair asset
    :return: integer amount for the sqrt price
    """
    precision = DECIMALS[asset_1] - DECIMALS[asset_2]
    return int(((price / 10 ** precision) ** 0.5) * 2 ** 96)


def calculate_price_from_sqrt_price(sqrt_price_x_96: int, asset_1: str, asset_2: str = 'USDC') -> float:
    """
    calculate the price for a given sqrt price for a base asset in terms of a pair asset
    :param sqrt_price_x_96: integer amount for sqrt price of asset 1 in terms of asset 2
    :param asset_1: str for the base asset
    :param asset_2: str for the pair asset
    :return: float amount for the price
    """
    price = (sqrt_price_x_96 / 2 ** 96) ** 2 * (UNIT_CONVERTER[asset_1] / UNIT_CONVERTER[asset_2])
    return price


def price_to_tick(price: float, asset: str) -> int:
    """
    calculate the tick value from a price for a given asset
    :param price: float amount for the price
    :param asset: str for the asset
    :return: tick value
    """
    sqrt_price_x_96 = calculate_sqrt_price(price, asset)
    return floor(log((sqrt_price_x_96 / 2 ** 96) ** 2) / log(1.0001))


def tick_to_price(tick: int, asset_1: str, asset_2: str = 'USDC') -> float:
    """
    calculate the price from a tick for a given asset in terms of the base asset
    :param tick: integer amount for the given tick
    :param asset_1: str for the base asset
    :param asset_2: str for the pair asset
    :return: price value
    """
    price = 1.0001 ** tick
    return price * (UNIT_CONVERTER[asset_1] / UNIT_CONVERTER[asset_2])


def hex_price_to_decimal(u256_hex_str: str, asset_1: str, asset_2: str = 'USDC') -> float:
    """
    convert a u256 hex string to a float number
    :param u256_hex_str: hex string representing a 128bit integer and 128bit fractional number
    :param asset_1: str for the base asset
    :param asset_2: str for the pair asset
    """
    # Convert hex string to integer
    u256_integer = int(u256_hex_str, 16)

    # Extract the integer part (the top 128 bits) & convert integer part to float
    float_integer = float(u256_integer >> 128)

    # Extract the fractional part (the bottom 128 bits) & convert fractional part to its decimal equivalent
    float_fractional = float(u256_integer & ((1 << 128) - 1)) / (1 << 128)

    # Combine and return the result
    return (float_integer + float_fractional) * (UNIT_CONVERTER[asset_1] / UNIT_CONVERTER[asset_2])


def hex_amount_to_decimal(hex_string: str, asset: str) -> float:
    """
    convert a hex string to a decimal number
    :param asset:
    :param hex_string:
    """
    return float(str((int(hex_string, 16)) / UNIT_CONVERTER[asset]))
