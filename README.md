# Chainflip Market Maker 

---

Welcome to the demo chainflip market maker. This is a simple market making bot for use with the Chainflip protocol. 

It is free to use and easy to modify with your own strategies or ideas. It has a modular design where any of the
elements can be edited in isolation if required. 

Currently, it is only configured for the testnet (partnernet - Goerli) and will be updated with the mainnet when launched.

The structure is as follows:

- **chainflip_env** - all code required for directly interacting with the Chainflip partnernet
    
  1. `chainflip_amm` - a dummy amm replicating the timings for Chainflip's amm (will be removed come mainnet)
  2. `chainflip_chain` - a simple replication of the Chainflip chain with relevant market making functions
  3. `commands` - all rpc commands needed for interacting with the Chainflip partnernet
  4. `pool` - dummy pool (does not currently have too many features, only needed for demo purposes)
  5. `swapping_channel` - swapping channels opened by the Chainflip chain


- **external_env**
  1. `data_stream` - access to Binance candles stream.
  2. `mem_pools` - monitoring of mempools. Currently only Ethereum mempool, more to come.


- **market_maker**
  1. `book` - simple order book
  2. `market_maker` - handler for the market making class, all other classes are imported here
  3. `wallet` - wallet handler 



## Set up

---

Please first go to this Github repo hosted by Chainflip: https://github.com/chainflip-io/chainflip-partnernet

Follow the instructions on this page. This sets up your local node using Docker. 

From within `chainflip/chainflip-partnernet` run:

`% docker compose up`

This will run the local node in your terminal window. You are now ready to send commands to partnernet. You should have something like below:
![Screenshot 2023-07-25 at 12 35 04](https://github.com/jit-strategies/chainflip-market-maker/assets/114564589/175c8635-e7fb-445f-9d81-694aacffcf85)


Next you will need to fund the account with some `tFLIP`, the  Chainflip testnet token. Funding the account is 
required before sending commands to the Chainflip partnernet.

Once this process is done, install the required packages (it is highly recommended to use a virtual env):

`% pip install -r requirements.txt`

Now in a separate terminal window run the following commands:

```
curl -H "Content-Type: application/json" \
    -d '{"id":"your_arbitrary_id", "jsonrpc":"2.0", "method": "lp_registerAccount", "params": [0]}' \
    http://localhost:10589
```

This sets up your lp account with the partnernet. You should receive something similar to the following: 
```
{"jsonrpc":"2.0","result":"0xabbaefb24bbd3727e24779c9d8449a213818c4d5e2df96ea06572f123154160a","id":"your_arbitrary_id"}%
```


Set up an emergency withdrawal address for the chain (Ethereum, Bitcoin and Polkadot). This is a failsafe for your assets! 
> Note, if you have set up an ETH emergency deposit, you do not need to do so again for any asset on that chain, e.g. Usdc or Flip. This only has to be done once. 
```
curl -H "Content-Type: application/json" \
    -d '{"id":"your_arbitrary_id", "jsonrpc":"2.0", "method": "lp_registerEmergencyWithdrawalAddress", "params": ["Ethereum", "0x..desired_wallet_address"]}' \
    http://localhost:10589
```
If successful you should get something like:
```
{"jsonrpc":"2.0","result":"0xbbb6…7499","id":"JIT"}%   
```

Once this is done, for any the asset you want to open a liquidity deposit address for run the following command (you can open as many liquidity deposit addresses as you wish):
```
curl -H "Content-Type: application/json" \
    -d '{"id":"your_arbitrary_id", "jsonrpc":"2.0", "method": "lp_liquidityDeposit", "params": ["Eth", "Usdc"]}' \
    http://localhost:10589
```
You now should get an address for the relevant chain. For the example above:
```
{"jsonrpc":"2.0","result":"0xac1323xxxxxxxxxxxxxxxxxxx","id":"your_arbitrary_id"}%
```

You can send the funds manually or through the wallet to the address given from above. 
To add your wallet, simply create and paste the private key into a `.env` file. Then add your infrua address in the settings file in `/utils`
> DO NOT SHARE THIS KEY WITH SOMEONE ELSE OR COMMIT IT TO THE REPO! 
```
ETH_WALLET_PRIVATE_KEY=795xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> A wallet is not required for the partnernet market maker. 

To check the available balance usable by Chainflip run: 
```
% curl -H "Content-Type: application/json" \
    -d '{"id":"your_arbitrary_id", "jsonrpc":"2.0", "method": "lp_assetBalances", "params": []}' \
    http://localhost:10589
```

which should return below, with the amount you deposited (Chainflip uses the smallest unit for its assets, e.g. gwei for Eth):
```
{"jsonrpc":"2.0","result":"{\"Flip\":0,\"Usdc\":10000000000,\"Dot\":0,\"Eth\":500000000000000000,\"Btc\":0}","id":"your_arbitrary_id"}% 
```
> If your assets are not there and you have received no errors, this could be down to the external chains being slow. Be patient but if there is still nothing after rerunning the above command after a few minutes, reach out and we can investigate.

Once you have deposited the assets into the Chainflip addresses, you are good to run the market maker. 

To run the market maker in any terminal (make sure you are in the correct folder `/chainflip_market_maker`):

`% python main.py --strategy stream`

or 

`% python main.py --strategy jit`

Both of these strategies can be edited easily. 

## Strategies

---

- ### stream 
  1. Receives a Binance candle data point every 30 seconds
  2. Mints a limit order based on the data point - alive for 30 seconds
  3. Mints a range order based on the current pool price - alive for 30 seconds
  4. Burns limit order - if filled fees are received
  5. Burns range order 
  6. Return to step i)

- ### jit
  1. Receives a Binance candle data point every 30 seconds
  2. Watch for swapping channels opened by the chainflip chain
  3. Monitor mempool for deposits into the above swapping channel
  4. Prepare limit order based on current data point and mint
  5. Prepare range order based on current pool data and mint
  6. Wait one Chainflip AMM block - 6 seconds
  7. Burn limit order
  8. Burn range order
  9. Return to step i)


## Sample Output

---

```
2023-07-20 14:00:27,123 - INFO - wallet - Initialised wallet handler for market maker - _is_connected = True
2023-07-20 14:00:27,123 - INFO - market_maker - Initialised Market Maker with id: JIT
2023-07-20 14:00:27,126 - INFO - strategy_stream - Initialised strategy: steaming quotes for 30 seconds
2023-07-20 14:00:27,615 - INFO - data_stream - Created new binance socket for klines with 1m interval: BinanceDataFeed: ETHUSDC 
2023-07-20 14:00:30,215 - INFO - data_stream - Received Binance candle: Binance Candle - start_time: 2023-07-20 14:00:00, end_time: 2023-07-20 14:00:59.999000, ticker: ETHUSDC, interval: 1m, open: 1916.27, close: 1916.27, high: 1916.27, low: 1916.27,volume: 0.0796
2023-07-20 14:00:51,132 - INFO - chainflip_amm - Executing swaps
2023-07-20 14:00:57,127 - INFO - market_maker - Chainflip v.PartnerNet: asset balances
2023-07-20 14:00:57,165 - INFO - market_maker - Current asset balances: {"Btc":0,"Eth":0,"Usdc":0,"Dot":0,"Flip":0}
2023-07-20 14:01:13,797 - INFO - strategy_stream - Open limit orders: {}
2023-07-20 14:01:13,797 - INFO - strategy_stream - Open range orders: {}
2023-07-20 14:00:57,165 - INFO - strategy_stream - Current pool price: 1916.1115243530448, current market price: 1916.27
2023-07-20 14:00:57,165 - INFO - strategy_stream - Created buy limit order candidate: Limit Order - Usdc: price = 1916.28, amount = 0.001, side = Side.BUY
2023-07-20 14:00:57,165 - INFO - market_maker - Chainflip v.PartnerNet: minting limit order - Limit Order - Usdc: price = 1916.28, amount = 0.001, side = Side.BUY
2023-07-20 14:01:13,789 - INFO - strategy_stream - Created range order candidate: Range Order - Usdc:, lower_price = 1906.1115243530448, upper_price = 1926.1115243530448, amount = 0.001
2023-07-20 14:01:13,789 - INFO - market_maker - Chainflip v.PartnerNet: minting range order - Range Order - Usdc:, lower_price = 1906.1115243530448, upper_price = 1926.1115243530448, amount = 0.001
2023-07-20 14:01:00,217 - INFO - data_stream - Received Binance candle: Binance Candle - start_time: 2023-07-20 14:00:00, end_time: 2023-07-20 14:00:59.999000, ticker: ETHUSDC, interval: 1m, open: 1916.27, close: 1916.26, high: 1916.27, low: 1916.26,volume: 0.8179
2023-07-20 14:01:03,134 - INFO - chainflip_amm - Executing swaps
```


## Note on simulator objects

There are several classes within this demonstrator that are very simple snapshots that attempt to simulate the output from the upcoming Chainflip mainnet. All will be removed when possible. As this demo is for market making and to show the LP API functionality they are not required to be in full to understand the market making process on Chainflip and to take the code you need for.

These classes are as follows:

`chainflip_amm` - demonstrates the timings for the Chainflip AMM. On partnernet there is no current AMM live, so this simulator is taken in its place.

`chainflip_chain` - demonstrates the communication from the Chainflip State Chain. Currently, on partnernet no Chain is communicated. 

`pool` - sets up a simple pool. No liquidity is within and only a price is tracked for simulation purposes. 

`swapping_channel` - a swapping channel object class that emulates the process for a swap on Chainflip. 
