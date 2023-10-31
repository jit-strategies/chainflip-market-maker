import asyncio

from chainflip_partnernet.external_env.mem_pools import MemPool
from chainflip_partnernet.external_env.data_stream import BinanceDataFeed

from chainflip_partnernet.chainflip_env.chainflip_chain import ChainflipChain
from chainflip_partnernet.chainflip_env.pool import Pool

from chainflip_partnernet.market_maker.market_maker import MarketMaker
from chainflip_partnernet.strategy.strategy_stream import StrategyStream
from chainflip_partnernet.strategy.strategy_jit import StrategyJIT


def run_stream_strategy():
    chainflip_sim = ChainflipChain(strategy='stream')

    btc_candles = BinanceDataFeed()
    btc_candles.create_new(asset='BTCUSDC')

    eth_candles = BinanceDataFeed()
    eth_candles.create_new(asset='ETHUSDC')

    btc_pool = Pool(btc_candles)
    eth_pool = Pool(eth_candles)

    candles = {
        'Btc': btc_candles,
        'Eth': eth_candles
    }

    pools = {
        'Btc': btc_pool,
        'Eth': eth_pool
    }

    market_maker = MarketMaker(chainflip=chainflip_sim, market_maker_id='JIT')

    strategy = StrategyStream(
        data_feeds=candles,
        active_pools=pools,
        market_maker=market_maker
    )

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                btc_candles(),
                eth_candles(),
                chainflip_sim.run(),
                #strategy.run_strategy(assets=['Eth', 'Btc'])
                strategy.run_strategy(assets=['Eth'])
            )
        )
    finally:
        loop.close()


def run_jit_strategy():
    eth_mempool = MemPool('Eth')
    chainflip_sim = ChainflipChain(strategy='jit')
    chainflip_sim.add_mem_pool(eth_mempool)

    binance_candles = BinanceDataFeed()
    binance_candles.create_new(asset='ETHUSDC')

    pool = Pool(binance_candles)

    market_maker = MarketMaker(chainflip=chainflip_sim, market_maker_id='JIT')

    strategy = StrategyJIT(
        base_asset='ETH',
        base_liquidity=1,
        quote_asset='USDC',
        quote_liquidity=1000,
        data_feed=binance_candles,
        pool=pool,
        market_maker=market_maker,
        mem_pool=eth_mempool
    )

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                binance_candles(),
                eth_mempool.watch(),
                chainflip_sim.run(),
                strategy.run_strategy()
            )
        )
    finally:
        loop.close()
