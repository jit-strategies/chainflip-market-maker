
import chainflip.utils.constants as CONSTANTS
import chainflip.utils.format as formatter
import chainflip.utils.logger as log

from chainflip.exchange.rpc import RpcCall
from chainflip.utils.data_types import LimitOrder, RangeOrder


logger = log.setup_custom_logger('root')


class OrderBook(object):
    """
    Simple order book.
    """
    def __init__(self, base_asset: str = "BTC", lp_id: str = None):
        self._base_asset = base_asset
        self._lp_id = lp_id
        self._bids = list()
        self._asks = list()
        self._range_orders = list()
        self._lp_open_orders = list()
        self._top_ask = None
        self._top_bid = None
        self._rpc_calls = RpcCall(lp_id)
        self._response = None

    @property
    def top_bid(self) -> LimitOrder:
        return self._top_bid

    @property
    def top_ask(self) -> LimitOrder:
        return self._top_ask

    @property
    def open_lp_orders(self):
        return self._lp_open_orders

    @top_bid.setter
    def top_bid(self, bid: float):
        self._top_bid = bid

    @top_ask.setter
    def top_ask(self, ask: float):
        self._top_ask = ask

    def _process_order_book(self, data: dict):
        bids = list()
        asks = list()

        for bid in data['limit_orders']['bids']:
            price = formatter.tick_to_price(bid['tick'], self._base_asset)
            amount = formatter.hex_amount_to_decimal(bid['sell_amount'], "USDC") / price
            if amount == 0:
                continue
            else:
                tmp = LimitOrder(
                    amount=amount,
                    price=formatter.tick_to_price(bid['tick'], self._base_asset),
                    base_asset=self._base_asset,
                    quote_asset='USDC',
                    id=bid['id'],
                    side=CONSTANTS.Side.BUY,
                    lp_account=bid['lp']
                )
                bids.append(tmp)
                if tmp.lp_account == self._lp_id:
                    self._lp_open_orders.append(tmp)

        for ask in data['limit_orders']['asks']:
            price = formatter.tick_to_price(ask['tick'], self._base_asset)
            amount = formatter.hex_amount_to_decimal(ask['sell_amount'], self._base_asset)
            if amount == 0:
                continue
            else:
                tmp = LimitOrder(
                    amount=amount,
                    price=price,
                    base_asset=self._base_asset,
                    quote_asset='USDC',
                    id=ask['id'],
                    side=CONSTANTS.Side.SELL,
                    lp_account=ask['lp']
                )
                asks.append(tmp)
                if tmp.lp_account == self._lp_id:
                    self._lp_open_orders.append(tmp)

        for range_order in data['range_orders']:
            tmp = RangeOrder(
                lower_price=formatter.tick_to_price(range_order['range']['start'], self._base_asset),
                upper_price=formatter.tick_to_price(range_order['range']['end'], self._base_asset),
                base_asset=self._base_asset,
                quote_asset='USDC',
                id=range_order['id'],
                type=CONSTANTS.RangeOrderType.LIQUIDITY,
                amount=range_order["liquidity"],
                lp_account=range_order['lp']
            )
            self._range_orders.append(tmp)
            if tmp.lp_account == self._lp_id:
                self._lp_open_orders.append(tmp)

        self._bids = sorted(bids, key=lambda x: x.price, reverse=True)
        self._asks = sorted(asks, key=lambda x: x.price)

        try:
            self.top_bid = self._bids[0]
        except IndexError:
            logger.info("No limit order bids in current order book")

        try:
            self._top_ask = self._asks[0]
        except IndexError:
            logger.info("No limit order asks in current order book")

    async def _rpc_update_orderbook(self):
        try:
            self._response = await self._rpc_calls(
                CONSTANTS.RPCCommands.PoolOrders,
                self._base_asset,
                "USDC",
            )

            self._process_order_book(data=self._response['result'])
        except Exception as e:
            raise e

    async def update(self):
        await self._rpc_update_orderbook()
