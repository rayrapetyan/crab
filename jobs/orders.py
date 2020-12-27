import datetime

import pandas as pd

from collections import (
    deque,
)

from typing import List

from jobs.conf import *

from utils.misc import timeit

from x.basex import (
    BaseX,
    Side as OrderSide,
    Symbol,
)

# last DATA_DAYS
SNAPSHOTS_LEN = int(DATA_DAYS * 24 * 3600 / GET_SNAPSHOT_INTERVAL) * \
                len(list(Symbol)) * \
                len(list(OrderSide)) * \
                4  # TODO: num of exchanges
orders_snapshots = deque(maxlen=SNAPSHOTS_LEN)


def get_snapshot(xchgs: List[BaseX]):
    ts = int(datetime.datetime.now().timestamp())
    for x in xchgs:
        for sym in list(Symbol):
            for side in list(OrderSide):
                orders = x.get_orders(symbol=sym, side=side)
                entry = [
                    ts,
                    type(x).__name__,
                    sym.name,
                    side.name,
                    orders,
                ]
                orders_snapshots.append(entry)


@timeit
def dump():
    # ts = int(datetime.datetime.now().timestamp())
    df = pd.DataFrame(orders_snapshots, columns=['ts', 'xname', 'sym', 'side', 'orders'])
    df.to_parquet(BASE_FOLDER / f'orders_v{DUMP_VERSION}.parquet', compression='gzip')
