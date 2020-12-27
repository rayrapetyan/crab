import copy
import numpy as np

from collections import (
    deque,
)
from enum import Enum
from typing import (
    List,
)

from autobahn.twisted.websocket import (
    connectWS,
)
from twisted.internet import ssl

from utils.order import (
    Order,
    OrdersBook,
)

from utils.trade import Trade
from utils.x_client import XClient

TRADES_POOL_SIZE = 100000

Side = Enum('Side', 'SELL BUY')

Symbol = Enum('Symbol', 'BTCUSD ETHUSD')

SYM_ROUNDX = {
    Symbol.ETHUSD: 5,
    Symbol.BTCUSD: 100,
}


class BaseX(XClient):
    def __init__(self, url):
        super().__init__(url)
        self.trades = {}
        self.orders_books = {}
        for s in list(Symbol):
            self.trades[s] = deque(maxlen=TRADES_POOL_SIZE)
            self.orders_books[s] = {}
            self.orders_books[s][Side.SELL] = OrdersBook([])
            self.orders_books[s][Side.BUY] = OrdersBook([])

    def order_book(self, symbol: Symbol, side: Side) -> OrdersBook:
        return self.orders_books[symbol][side]

    def init_orders(self, symbol: Symbol, side: Side, orders: List[Order]):
        self.order_book(symbol, side).init(orders)

    def get_orders(self, symbol: Symbol, side: Side, roundx: int = None, limit: int = 10000) -> np.ndarray:
        if not roundx:
            roundx = SYM_ROUNDX[symbol]
        if side == Side.BUY:
            roundx *= -1
        return self.order_book(symbol, side).get_orders(roundx=roundx, head=(side == Side.BUY), limit=limit)

    def upd_orders(self, symbol: Symbol, side: Side, order: Order):
        self.order_book(symbol, side).upd(order)

    def get_trades(self, symbol):
        return self.trades[symbol]

    def init_trades(self, trades: List[Trade]):
        pass

    def flush_trades(self, symbol):
        orig_trades = self.get_trades(symbol)
        res = copy.deepcopy(orig_trades)
        orig_trades.clear()
        return res

    def upd_trades(self, symbol: Symbol, trade: Trade):
        self.get_trades(symbol).appendleft(trade)

    def on_open(self):
        raise NotImplementedError()

    def on_message(self):
        raise NotImplementedError()

    def run(self):
        options = ssl.optionsForClientTLS(hostname=self.host)
        # options = ssl.ClientContextFactory()
        connectWS(self, options)
