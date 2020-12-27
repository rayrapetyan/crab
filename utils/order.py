import numpy as np
import pandas as pd

from dataclasses import dataclass
from typing import (
    List,
)


@dataclass
class Order:
    price: float
    size: float


class OrdersBook:
    def __init__(self, data: List[Order]):
        self.book = {}
        if data:
            self.init(data)

    def init(self, orders: List[Order]):
        for o in orders:
            self.book[o.price] = o.size

    def upd(self, order: Order):
        try:
            if order.size == 0:
                self.book.pop(order.price)
            else:
                self.book[order.price] = order.size
        except Exception as e:
            pass
            # import traceback
            # track = traceback.format_exc()
            # print(track)
            """
            print(f'price not found in book: '
                  f'price: {order.price}, '
                  f'size: {order.size}, '
                  f'maxprice: {self.book.index.max()}, '
                  f'minprice: {self.book.index.min()}')
            """

    def get_orders(self, roundx: int = 0, head: bool = True, limit: int = 10000):
        b = pd.DataFrame(
            {'price': self.book.keys(), 'size': self.book.values()},
            columns=['price', 'size']
        )
        if roundx:
            if roundx < 0:
                f = np.floor
                roundx *= -1
            else:
                f = np.ceil
            b['price'] = (b['price'] / roundx).apply(f).astype(int) * roundx
        b = b.groupby('price')['size'].sum().sort_index(ascending=False).reset_index()
        if head:
            b = b.head(limit).to_numpy()
        else:
            b = b.tail(limit).to_numpy()
        return b.tolist()
