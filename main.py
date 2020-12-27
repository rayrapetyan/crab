"""
# warn: do not change order below ----------
from pyqtgraph.Qt import QtGui
app = QtGui.QApplication([])
import qt5reactor
qt5reactor.install()
# end warn ---------------------------------

import pyqtgraph as pg
pg.setConfigOptions(antialias=True)

from dashboard import Dashboard
"""

import sys

from twisted.internet import (
    defer,
    reactor,
    task,
)
from twisted.python import log

from x.binance import Binance
from x.bitfinex import Bitfinex
from x.coinbase import Coinbase
from x.kraken import Kraken

from jobs.conf import *
from jobs.orders import (
    dump as dump_orders,
    get_snapshot as get_snapshot_orders,
)
from jobs.trades import (
    dump as dump_trades,
    get_snapshot as get_snapshot_trades,
)

# defer.setDebugging(True) WARNING: eats a LOT of CPU
log.startLogging(sys.stdout)

xchgs = [Coinbase(), Binance(), Bitfinex(), Kraken()]
#xchgs = [Kraken()]
for x in xchgs:
    x.run()

"""
app.setStyle('Fusion')
app.setFont(QtGui.QFont("Courier", 8))
d = Dashboard(xchgs, reactor)
d.show()
"""

j1 = task.LoopingCall(get_snapshot_orders, xchgs)
j1.start(GET_SNAPSHOT_INTERVAL)

j2 = task.LoopingCall(dump_orders)
j2.start(DUMP_INTERVAL)

j3 = task.LoopingCall(get_snapshot_trades, xchgs)
j3.start(GET_SNAPSHOT_INTERVAL)

j4 = task.LoopingCall(dump_trades)
j4.start(DUMP_INTERVAL)

reactor.run()
