import asyncio
import signal

from chainflip.data.binance import BinanceDataFeed
from chainflip.market_maker.order_management import OMS
from chainflip.market_maker.pool_handler import ChainflipPools
from chainflip.strategy.stream_prices import StrategyStream


async def run_stream_strategy(maker_id: str):
    market_maker_id = maker_id
    lp_id = 'cFPdef3hF5zEwbWUG6ZaCJ3X7mTvEeAog7HxZ8QyFcCgDVGDM'

    eth_candles = BinanceDataFeed()
    eth_candles.create_new(asset='ETHUSDC')
    candles = {
        'ETH': eth_candles,
    }

    pools = ChainflipPools(user_id=market_maker_id, lp_id=lp_id)
    pools.add_pool(base_asset='ETH', quote_asset='USDC')

    oms = OMS(
        market_maker_id,
        lp_id,
        erc20_withdrawal_address='0xe086a97042498dac883c58bcafef57f5a13bab7e',
        btc_withdrawal_address='bcrt1p9em7lf26vf9df34s39gnwlrjqu547hx4wmlxt5h4nqwg9jqn0gcqaakg70'
    )

    strategy = StrategyStream(
        lp_account=lp_id,
        base_asset='ETH',
        data_feed=candles,
        oms=oms,
        perseverance_pools=pools,
        active_order_time=18
    )

    try:
        await asyncio.gather(
            eth_candles(),
            strategy.run_strategy()
        )
    except asyncio.CancelledError:
        print("Tasks cancelled. Starting cleanup.")
        # Put your cleanup code here
        await strategy.update_order_book()
        await strategy._oms.check_order_book_and_cancel(strategy._order_book.open_lp_orders)
        await asyncio.sleep(6)
        print("Cleanup completed.")
    finally:
        # Any additional cleanup if needed
        print("Finalizing shutdown.")