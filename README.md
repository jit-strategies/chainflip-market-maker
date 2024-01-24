# Chainflip Market Maker 

---

Welcome to the demo chainflip market maker. This is a simple market making bot for use with the Chainflip protocol. 

This is a free to use system and easy to modify with your own strategies or ideas. It has a modular design where any of the elements can be edited in isolation if required. 

DISCLAIMER: THIS IS A DEMONSTRATION. WHILE IT CAN RUN ON TESTNET AND MAINNET, BE SURE TO UNDERSTAND THE RISKS WITH DEPLOYING CAPITAL ON A LIVE DEX. WE TAKE NO RESPONSIBILITY FOR LOSS OF CAPITAL.

We advise you to test on testnet first and make the necessary adjustments you require before turning it onto mainnet. Deploying the system directly without editing will most likely lose you money!

Currently, it is configured to read a node running locally, this can be any node: Mainnet, Testnet or Localnet. This can be done on a cloud server, e.g. AWS or your pc.

The setup below is for the Perseverance Testnet, but can also be run on Mainnet with no editing by downloading the Berghain mainnet api binaries instead of the Perseverance testnet ones.

There are several limitations to the default system, mainly in strategy. This demo only streams prices for 3 blocks (18 seconds) and then cancels them. It is primarily desinged to give you all the basic tooling required to design your own strategies!

## Set up

---

Please first go to this Github repo hosted by Chainflip: https://github.com/chainflip-io/chainflip-perseverance

Follow the instructions on this page. This sets up your local node using Docker. 

From within `chainflip/chainflip-perseverance` run:

`% docker compose up`

This will run the local node in your terminal window. You are now ready to send commands to perseverance. You should have something like below:
![Screenshot 2023-07-25 at 12 35 04](https://github.com/jit-strategies/chainflip-market-maker/assets/114564589/175c8635-e7fb-445f-9d81-694aacffcf85)

Next you will need to fund the account with some `tFLIP`, the  Chainflip testnet token. Funding the account is 
required before sending commands to the Chainflip Testnet. This is detailed in the chainflip repo (link above).

Once this process is done, install the required packages (it is highly recommended to use a virtual env):

`% pip install -r requirements.txt`

Now in a separate terminal window run the following commands:

```
curl -H "Content-Type: application/json" \
    -d '{"id":"your_arbitrary_id", "jsonrpc":"2.0", "method": "lp_registerAccount", "params": [0]}' \
    http://localhost:10589
```

This sets up your lp account with the perseverance. You should receive something similar to the following: 
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

> A wallet is not required for the perseverance market maker. 

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

`% python main.py`

## Troubleshooting

If you are getting errors like this one:
```
chainflip-perseverance-lp-1    | 2024-01-17T20:36:35.786724Z ERROR task_scope: parent task ended by error 'Your Chainflip account cFLjyVttoqqdRswqL2PNFwwUEpgytGQY8cxBPgvXiA8KKRohy is not funded': 'api/bin/chainflip-lp-api/src/main.rs:694:5'
chainflip-perseverance-lp-1    | 2024-01-17T20:36:35.788808Z ERROR task_scope: closed by error Your Chainflip account cFLjyVttoqqdRswqL2PNFwwUEpgytGQY8cxBPgvXiA8KKRohy is not funded: 'api/bin/chainflip-lp-api/src/main.rs:694:5'
chainflip-perseverance-lp-1    | Error: Your Chainflip account cFLjyVttoqqdRswqL2PNFwwUEpgytGQY8cxBPgvXiA8KKRohy is not funded
```

Your account is not funded. Please go to the Chainflip Auctions page to register a node and fund it. 


