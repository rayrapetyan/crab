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
    'tETHUSD': Symbol.ETHUSD,
    'tBTCUSD': Symbol.BTCUSD,
}

WS_FEED = 'wss://api-pub.bitfinex.com/ws/2'
PRODUCT_IDS = [k for k in SYM_MAP.keys()]
WS_CHANNELS = ['trades', 'book']

TRADE_CHANNEL_IDS = {}
BOOK_CHANNEL_IDS = {}


# TODO: notifies only about +\- 200 orders
class Bitfinex(BaseX):
    def __init__(self):
        super().__init__(WS_FEED)

    def init_order_books(self, orders, symbol):
        self.init_orders(SYM_MAP[symbol], OrderSide.SELL,
                         [Order(float(x[0]), float(x[1] * -1)) for x in orders if x[2] < 0])
        self.init_orders(SYM_MAP[symbol], OrderSide.BUY,
                         [Order(float(x[0]), float(x[1])) for x in orders if x[2] > 0])

    def handle_orders_msg(self, order, symbol):
        sym = SYM_MAP[symbol]
        price = order[0]
        size = order[2]
        side = OrderSide.BUY if size > 0 else OrderSide.SELL
        num_orders = order[1]
        if num_orders == 0:
            size = 0
        elif side == OrderSide.SELL:
            size *= -1
        if size != 0:
            self.upd_orders(sym, side, Order(price, size))

    def handle_trade_msg(self, trade, symbol):
        sym = SYM_MAP[symbol]
        ts = int(trade[1] / 1000)
        size = trade[2]
        price = trade[3]
        self.upd_trades(sym, Trade(ts, size, price))

    def on_message(self, message):
        if isinstance(message, dict):
            if message['event'] == 'subscribed':
                sym = message['symbol']
                if message['channel'] == 'trades':
                    TRADE_CHANNEL_IDS[message['chanId']] = sym
                elif message['channel'] == 'book':
                    BOOK_CHANNEL_IDS[message['chanId']] = sym
            return

        if not isinstance(message, list):
            return

        channel_id = message[0]

        if channel_id in BOOK_CHANNEL_IDS:
            sym = BOOK_CHANNEL_IDS[channel_id]
            if len(message) == 2:
                if isinstance(message[1], str) and message[1] == 'hb':
                    return
                elif isinstance(message[1], list) and len(message[1]) == 3:
                    self.handle_orders_msg(message[1], sym)
                    return
                elif isinstance(message[1], list) and \
                        isinstance(message[1][0], list) and \
                        len(message[1][0]) == 3:
                    self.init_order_books(message[1], sym)
            return
        elif channel_id in TRADE_CHANNEL_IDS:
            sym = TRADE_CHANNEL_IDS[channel_id]
            if len(message) == 3:
                if message[1] == 'te':
                    self.handle_trade_msg(message[2], sym)
                    return
                elif message[1] == 'tu':
                    return
            elif isinstance(message[1], list) and \
                    isinstance(message[1][0], list) and \
                    len(message[1][0]) == 4:
                # TODO: init trades
                return

        else:
            return
            raise Exception(f"unknown message: {message}")

    def on_open(self):
        for p in PRODUCT_IDS:
            msg = {
                'event': 'subscribe',
                'symbol': p,
                'channel': 'trades'
            }
            self.send_message(msg)
            msg = {
                'event': 'subscribe',
                'symbol': p,
                'channel': 'book',
                'freq': 'F1',
                'prec': 'P0',
                'len': 100
            }
            self.send_message(msg)
