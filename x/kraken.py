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
    'ETH/USD': Symbol.ETHUSD,
    'XBT/USD': Symbol.BTCUSD,
}

WS_FEED = 'wss://ws.kraken.com'
PRODUCT_IDS = [k for k in SYM_MAP.keys()]

DEPTH = 1000


class Kraken(BaseX):
    def __init__(self):
        super().__init__(WS_FEED)

    def init_orders_books(self, type, orders, symbol):
        if type == 'a':
            self.init_orders(symbol, OrderSide.SELL, [Order(float(x[0]), float(x[1])) for x in orders])
        elif type == 'b':
            self.init_orders(symbol, OrderSide.BUY, [Order(float(x[0]), float(x[1])) for x in orders])
        else:
            raise Exception(f"unknown type: {type}")

    def handle_orders_msg(self, orders, sym):
        symbol = SYM_MAP[sym]
        if 'a' in orders:
            orders_ = orders['a']
            for o in orders_:
                self.upd_orders(symbol, OrderSide.SELL, Order(float(o[0]), float(o[1])))
        elif 'as' in orders:
            orders_ = orders['as']
            self.init_orders_books('a', orders_, symbol)
        if 'b' in orders:
            orders_ = orders['b']
            for o in orders_:
                self.upd_orders(symbol, OrderSide.BUY, Order(float(o[0]), float(o[1])))
        elif 'bs' in orders:
            orders_ = orders['bs']
            self.init_orders_books('b', orders_, symbol)

    def handle_trade_msg(self, trades, sym):
        symbol = SYM_MAP[sym]
        for trade in trades:
            ts = int(float(trade[2]))
            size = float(trade[1])
            price = float(trade[0])
            side = trade[3]
            if side == 'b':
                size *= -1
            self.upd_trades(symbol, Trade(ts, size, price))

    def on_message(self, message):
        if not isinstance(message, list):
            return
        if len(message) == 4 and message[2] == 'trade':
            self.handle_trade_msg(message[1], message[3])
        elif len(message) == 4:
            self.handle_orders_msg(message[1], message[3])
        elif len(message) == 5:
            # when both 'a' and 'b' are present
            self.handle_orders_msg(message[1], message[4])
            self.handle_orders_msg(message[2], message[4])
        else:
            raise Exception(f"unknown message: {message}")

    def on_open(self):
        msg = {
            'event': 'subscribe',
            'pair': PRODUCT_IDS,
            'subscription': {
                'name': 'trade',
            }
        }
        self.send_message(msg)

        msg['subscription'] = {
            'name': 'book',
            'depth': DEPTH
        }
        self.send_message(msg)
