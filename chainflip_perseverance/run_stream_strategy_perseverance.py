import asyncio

from chainflip_perseverance.data.binance import BinanceDataFeed
from chainflip_perseverance.market_maker.market_maker import OMS
from chainflip_perseverance.market_maker.perseverance_pools import PerseverancePools
from chainflip_perseverance.strategy.stream_prices import StrategyStream


def run_stream_strategy(maker_id: str):
    """
    run stream strategy for Btc / Usdc and Eth / Usdc pools
    """
    market_maker_id = maker_id
    lp_id = 'cFPdef3hF5zEwbWUG6ZaCJ3X7mTvEeAog7HxZ8QyFcCgDVGDM'
    assets = ['Btc', 'Eth']

    btc_candles = BinanceDataFeed()
    btc_candles.create_new(asset='BTCUSDC')
    eth_candles = BinanceDataFeed()
    eth_candles.create_new(asset='ETHUSDC')
    candles = {
        'Btc': btc_candles,
        'Eth': eth_candles
    }

    pools = PerseverancePools(user_id=market_maker_id, lp_id=lp_id)
    pools.add_pool(base_asset='Eth', pair_asset='Usdc')
    pools.add_pool(base_asset='Btc', pair_asset='Usdc')

    oms = OMS(
        market_maker_id,
        erc20_withdrawal_address='0xe086a97042498dac883c58bcafef57f5a13bab7e',
        btc_withdrawal_address='bcrt1p9em7lf26vf9df34s39gnwlrjqu547hx4wmlxt5h4nqwg9jqn0gcqaakg70'
    )

    strategy = StrategyStream(
        data_feed=candles,
        oms=oms,
        perseverance_pools=pools,
        active_order_time=30
    )

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                btc_candles(),
                eth_candles(),
                strategy.run_strategy(assets)
            )
        )
    finally:
        loop.close()
