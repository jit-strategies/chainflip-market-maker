from enum import Enum

version = 'PartnerNet'


class CommandMap(Enum):
    Empty = ''
    Register = 'lp_registerAccount'
    LiquidityDeposit = 'lp_liquidityDeposit'
    WithdrawAsset = 'lp_withdrawAsset'
    AssetBalances = 'lp_assetBalances'
    RangeOrders = 'lp_getRangeOrders'
    LimitOrders = 'lp_getLimitOrders'
    MintRangeOrderLiquidity = 'lp_mintRangeOrder_liquidity'
    MintRangeOrderAssetAmounts = 'lp_mintRangeOrder_assetAmount'
    BurnRangeOrder = 'lp_burnRangeOrder'
    MintLimitOrder = 'lp_mintLimitOrder'
    BurnLimitOrder = 'lp_burnLimitOrder'


ASSETS = {
    'USDC': 'Usdc',
    'ETH': 'Eth',
    'BTC': 'Btc',
    'DOT': 'Dot'
}


class Side(Enum):
    BUY = 'Buy',
    SELL = 'Sell',
    NONE = 'None',


class RangeOrderType(Enum):
    LIQUIDITY = 'liquidity_range'
    ASSET_AMOUNTS_STABLE = 'asset_stable_usdc'
    ASSET_AMOUNTS_UNSTABLE = 'asset_unstable'


DECIMALS = {
    'Dot': 10,
    'Eth': 18,
    'Btc': 8,
    'Usdc': 6
}

UNIT_CONVERTER = {
    'Usdc': 10 ** 6,
    'Eth': 10 ** 18,
    'Btc': 10 ** 8,
    'Dot': 10 ** 10,
    'Flip': 10 ** 18
}

TICK_SIZE = 2

BLOCK_TIMINGS = {
    'Chainflip': 6,
    'Bitcoin': 30,
    'Btc': 30,
    'Ethereum': 12,
    'Eth': 12,
    'Polkadot': 6,
    'Dot': 6
}

EXCHANGE_RATES = {
    ('Eth', 'Usdc'): 2000,
    ('Btc', 'Usdc'): 30000,
    ('Dot', 'Usdc'): 20,
    ('Eth', 'Btc'): 0.05,
    ('Btc', 'Eth'): 16
}


GAS = 21000
GAS_PRICE = 30  # in gwei


TOKEN_CONTRACT_ADDRESS = {
    'Dai': '0xdc31Ee1784292379Fbb2964b3B9C4124D8F89C60',
    'Usdc': '0x07865c6E87B9F70255377e024ace6630C1Eaa37F',
    'Eth': '0xB4FBF271143F4FBf7B91A5ded31805e42b2208d6'
}
