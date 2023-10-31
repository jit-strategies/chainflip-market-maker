import asyncio

from chainflip_perseverance.data.binance import BinanceDataFeed
from chainflip_perseverance.market_maker.market_maker import OMS
from chainflip_perseverance.market_maker.perseverance_pools import PerseverancePools
from chainflip_perseverance.market_maker.prewitness_swaps import Prewitnesser
from chainflip_perseverance.strategy.just_in_time import StrategyJIT


def run_jit_strategy(maker_id: str):
    """
    run jit strategy for Eth / Usdc pool
    """
    market_maker_id = maker_id
    lp_id = 'cFPdef3hF5zEwbWUG6ZaCJ3X7mTvEeAog7HxZ8QyFcCgDVGDM'

    eth_candles = BinanceDataFeed()
    eth_candles.create_new(asset='ETHUSDC')
    candles = {
        'Eth': eth_candles
    }

    pools = PerseverancePools(user_id=market_maker_id, lp_id=lp_id)
    pools.add_pool(base_asset='Eth', pair_asset='Usdc')

    oms = OMS(
        market_maker_id,
        erc20_withdrawal_address='0xe086a97042498dac883c58bcafef57f5a13bab7e',
    )

    prewitnesser = Prewitnesser(user_id=market_maker_id)

    strategy_eth = StrategyJIT(
        base_asset='Eth',
        pair_asset='Usdc',
        data_feed=candles,
        oms=oms,
        perseverance_pools=pools,
        prewitnesser=prewitnesser
    )

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                eth_candles(),
                strategy_eth.run_strategy()
            )
        )
    finally:
        loop.close()
