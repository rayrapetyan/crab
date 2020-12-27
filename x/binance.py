import requests

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
    'ETHUSDT': Symbol.ETHUSD,
    'BTCUSDT': Symbol.BTCUSD,
}
PRODUCT_IDS = [k.lower() for k in SYM_MAP.keys()]
WS_CHANNELS = ['trade', 'depth']

STREAMS = []
for p in PRODUCT_IDS:
    for c in WS_CHANNELS:
        stream = f'{p}@{c}'
        if c == 'depth':
            stream += '@1000ms'
        STREAMS.append(stream)
WS_FEED = f'wss://stream.binance.com:9443/stream?streams={"/".join(STREAMS)}'


# https://github.com/binance-exchange/binance-official-api-docs/blob/master/web-socket-streams.md
class Binance(BaseX):
    def __init__(self):
        super().__init__(WS_FEED)

    def init_orders_books(self):
        url = "https://api.binance.com/api/v3/depth"
        for symbol in SYM_MAP.keys():
            params = {
                'symbol': symbol,
                'limit': 5000,
            }
            s = requests.session()
            snapshot = s.get(url=url, params=params).json()
            self.init_orders(SYM_MAP[symbol], OrderSide.SELL,
                             [Order(float(x[0]), float(x[1])) for x in snapshot['asks']])
            self.init_orders(SYM_MAP[symbol], OrderSide.BUY,
                             [Order(float(x[0]), float(x[1])) for x in snapshot['bids']])

    def handle_orders_msg(self, orders) -> None:
        symbol = SYM_MAP[orders['s']]
        for a in orders['a']:
            self.upd_orders(symbol, OrderSide.SELL, Order(float(a[0]), float(a[1])))
        for b in orders['b']:
            self.upd_orders(symbol, OrderSide.BUY, Order(float(b[0]), float(b[1])))

    def handle_trade_msg(self, trade):
        symbol = SYM_MAP[trade['s']]
        price = float(trade['p'])
        size = float(trade['q'])
        if not trade['m']:
            size *= -1
        ts = int(trade['T'] / 1000)
        self.upd_trades(symbol, Trade(ts, size, price))

    def on_message(self, message):
        stream_meta = message['stream'].split('@')
        symbol = stream_meta[0]
        channel = stream_meta[1]
        if channel == 'trade':
            self.handle_trade_msg(message['data'])
        elif channel == 'depth':
            self.handle_orders_msg(message['data'])
        else:
            raise Exception(f"unknown channel: {channel}")

    def on_open(self):
        return

    def run(self):
        self.init_orders_books()
        super().run()
