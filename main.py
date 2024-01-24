import asyncio
import signal

from chainflip.run_stream_strategy_perseverance import run_stream_strategy


def main():
    mm_id = "JIT"
    loop = asyncio.get_event_loop()

    async def graceful_shutdown(sig, loop):
        print(f"Received exit signal {sig.name}, shutting down gracefully...")
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        loop.stop()

    for sig in [signal.SIGINT, signal.SIGTERM]:
        loop.add_signal_handler(sig, lambda: asyncio.create_task(graceful_shutdown(sig, loop)))

    loop.run_until_complete(run_stream_strategy(mm_id))


if __name__ == '__main__':
    main()
