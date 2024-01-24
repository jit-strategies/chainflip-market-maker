import asyncio
import json
import websockets


async def listen_to_websocket(url: str = "ws://localhost:9944"):
    data = {
        "id": "1",
        "jsonrpc": "2.0",
        "method": "cf_subscribe_prewitness_swaps",
        "params": ["USDC", "ETH"]
    }

    async with websockets.connect(url) as websocket:
        await websocket.send(json.dumps(data))

        # Discard the first element from the subscription
        await websocket.recv()

        # Listen for incoming messages
        try:
            while True:
                resp = await websocket.recv()
                resp = json.loads(resp)
                print(f"Swap USDC -> ETH {resp}")

        except websockets.ConnectionClosed as e:
            print(f'Pool price connection closed')

        except Exception as e:
            print(f'Pool price stream error occurred')


async def main():
    await listen_to_websocket()


if __name__ == '__main__':
    asyncio.run(main())
