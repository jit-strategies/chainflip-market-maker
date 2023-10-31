from enum import Enum

version = 'Perseverance'


class APICommands(Enum):
    Empty = 0
    Register = 1
    LiquidityDeposit = 2
    RegisterWithdrawalAddress = 3
    WithdrawAsset = 4
    AssetBalances = 5
    UpdateRangeOrderByLiquidity = 6
    UpdateRangeOrderByAmounts = 7
    SetRangeOrderByLiquidity = 8
    SetRangeOrderByAmounts = 9
    UpdateLimitOrder = 10
    SetLimitOrder = 11
    GetOpenSwapChannels = 12


class RPCCommands(Enum):
    Empty = 0
    RequiredRatioForRangeOrder = 3
    PoolInfo = 4
    PoolDepth = 5
    PoolLiquidity = 6
    PoolOrders = 7
    PoolRangeOrdersLiquidityValue = 8


class StreamCommands(Enum):
    Empty = 0
    SubscribePoolPrice = 1
    SubscribePreWitnessedSwaps = 2


class NetworkStatus(Enum):
    STOPPED = 0
    NOT_CONNECTED = 1
    CONNECTED = 2


class Chains(Enum):
    Ethereum = 'Ethereum'
    Bitcoin = 'Bitcoin'
    Polkadot = 'Polkadot'


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


class IncreaseOrDecreaseOrder(Enum):
    INCREASE = "Increase",
    DECREASE = "Decrease"


class RangeOrderType(Enum):
    LIQUIDITY = 1
    ASSET = 2


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
    'Bitcoin': 600,
    'Btc': 600,
    'Ethereum': 6,
    'Eth': 6,
    'Polkadot': 6,
    'Dot': 6,
    'Usdc': 6
}

CHAINFLIP_BLOCK_CONFIRMATIONS = {
    'Ethereum': 8,  # i.e. 8 blocks at 6 secs a block
    'Eth': 8,
    'Bitcoin': 1,  # i.e. 7 blocks at 600 secs (10 mins) a block - on mainnet btc = 6 blocks
    'Btc': 1,
}

GAS = 21000
GAS_PRICE = 30  # in gwei


TOKEN_CONTRACT_ADDRESS = {
    'Dai': '0xdc31Ee1784292379Fbb2964b3B9C4124D8F89C60',
    'Usdc': '0x07865c6E87B9F70255377e024ace6630C1Eaa37F',
    'Eth': '0xB4FBF271143F4FBf7B91A5ded31805e42b2208d6'
}
