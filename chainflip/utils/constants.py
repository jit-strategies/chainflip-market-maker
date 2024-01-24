from enum import Enum

version = 'Perseverance'


class APICommands(Enum):
    Empty = 0
    Register = 1
    LiquidityDeposit = 2
    RegisterWithdrawalAddress = 3
    WithdrawAsset = 4
    AssetBalances = 5
    SetRangeOrderByLiquidity = 8
    SetRangeOrderByAmounts = 9
    UpdateLimitOrder = 10
    SetLimitOrder = 11
    GetOpenSwapChannels = 12


class RPCCommands(Enum):
    Empty = 0
    AccountInfo = 1
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
    'USDC': 'USDC',
    'ETH': 'ETH',
    'BTC': 'BTC',
    'DOT': 'DOT'
}


class Side(Enum):
    BUY = 'Buy',
    SELL = 'Sell',
    NONE = 'None',


class IncreaseOrDecreaseOrder(Enum):
    INCREASE = "Increase",
    DECREASE = "Decrease"


class WaitForOption(Enum):
    NO_WAIT = "NoWait"
    IN_BLOCK = "InBlock"
    FINALIZED = "Finalized"


class RangeOrderType(Enum):
    LIQUIDITY = 1
    ASSET = 2


DECIMALS = {
    'DOT': 10,
    'ETH': 18,
    'FLIP': 18,
    'BTC': 8,
    'USDC': 6
}

UNIT_CONVERTER = {
    'USDC': 10 ** 6,
    'ETH': 10 ** 18,
    'BTC': 10 ** 8,
    'DOT': 10 ** 10,
    'FLIP': 10 ** 18
}

TICK_SIZE = 2

BLOCK_TIMINGS = {
    'Chainflip': 6,
    'Bitcoin': 600,
    'BTC': 600,
    'Ethereum': 6,
    'ETH': 6,
    'Polkadot': 6,
    'DOT': 6,
    'USDC': 6
}

CHAINFLIP_BLOCK_CONFIRMATIONS = {
    'Ethereum': 8,  # i.e. 8 blocks at 6 secs a block
    'ETH': 8,
    'Bitcoin': 3,  # i.e. 3 blocks at 600 secs (10 mins) a block - on mainnet btc = 3 blocks
    'BTC': 3,
}
