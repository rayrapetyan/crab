import datetime
import pytz

from utils.order import (
    Order,
)
from utils.trade import Trade
from x.basex import (
    BaseX,
    Side as OrderSide,
    Symbol,
)

SYM_MAP = {
    'ETH-USD': Symbol.ETHUSD,
    'BTC-USD': Symbol.BTCUSD,
}

WS_FEED = 'wss://ws-feed.pro.coinbase.com'
PRODUCT_IDS = [k for k in SYM_MAP.keys()]
WS_CHANNELS = ['level2', 'matches']


class Coinbase(BaseX):
    def __init__(self):
        super().__init__(WS_FEED)

    def init_orders_books(self, snapshot):
        symbol = SYM_MAP[snapshot['product_id']]
        self.init_orders(symbol, OrderSide.SELL,
                         [Order(float(x[0]), float(x[1])) for x in snapshot['asks']])
        self.init_orders(symbol, OrderSide.BUY,
                         [Order(float(x[0]), float(x[1])) for x in snapshot['bids']])

    def handle_orders_msg(self, order) -> None:
        symbol = SYM_MAP[order['product_id']]
        changes = order['changes']
        for c in changes:
            op = c[0]
            price = float(c[1])
            size = float(c[2])
            if op == 'buy':
                side = OrderSide.BUY
            elif op == 'sell':
                side = OrderSide.SELL
            else:
                raise Exception(f"unknown op: {op}")
            self.upd_orders(symbol, side, Order(price, size))
        return

    def handle_trade_msg(self, trade):
        symbol = SYM_MAP[trade['product_id']]
        price = float(trade['price'])
        size = float(trade['size'])
        if trade['side'] == 'buy':
            size *= -1
        ts = datetime.datetime.strptime(trade["time"][:19], "%Y-%m-%dT%H:%M:%S")
        ts = int(ts.replace(tzinfo=pytz.UTC).timestamp())
        self.upd_trades(symbol, Trade(ts, size, price))

    def on_message(self, message):
        if message['type'] == 'snapshot':
            self.init_orders_books(message)
        elif message['type'] == 'l2update':
            self.handle_orders_msg(message)
        elif message['type'] == 'match':
            self.handle_trade_msg(message)

    def on_open(self):
        msg_subscribe = {
            'type': 'subscribe',
            'product_ids': PRODUCT_IDS,
            'channels': WS_CHANNELS
        }
        self.send_message(msg_subscribe)
