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
    Symbol,
)

# last 5 days
SNAPSHOTS_LEN = int(DATA_DAYS * 24 * 3600 / GET_SNAPSHOT_INTERVAL) * \
                len(list(Symbol)) * \
                4  # TODO: num of exchanges
trades_snapshots = deque(maxlen=SNAPSHOTS_LEN)


def get_snapshot(xchgs: List[BaseX]):
    ts = int(datetime.datetime.now().timestamp())
    for x in xchgs:
        for sym in list(Symbol):
            trades = x.flush_trades(symbol=sym)
            entry = [
                ts,
                type(x).__name__,
                sym.name,
                [x.price for x in trades],
            ]
            trades_snapshots.append(entry)


@timeit
def dump():
    # ts = int(datetime.datetime.now().timestamp())
    df = pd.DataFrame(trades_snapshots, columns=['ts', 'xname', 'sym', 'trades'])
    df.to_parquet(BASE_FOLDER / f'trades_v{DUMP_VERSION}.parquet', compression='gzip')
