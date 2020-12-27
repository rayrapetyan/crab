import pyqtgraph as pg

from pyqtgraph.Qt import (
    QtCore,
    QtGui,
)

from x.basex import (
    BaseX,
    TRADES_LEN,
)

REFRESH_PERIOD = 1*5000

LABEL_ROW = 0
ASKS_BOOK_ROW = 1
BIDS_BOOK_ROW = 2
PRICE_CHART_ROW = 3
TRADES_ROW = 4


class Dashboard(pg.GraphicsWindow):
    def __init__(self, xchgs, reactor, parent=None):
        super().__init__(parent)
        self.xchgs = xchgs
        self.reactor = reactor
        self.create_main_window()

        self.refresh_timer = QtCore.QTimer()
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(REFRESH_PERIOD)


    def create_main_window(self):
        self.setWindowTitle('crab')
        layout = QtGui.QGridLayout()
        self.layout = layout
        self.setLayout(layout)

        for i, x in enumerate(self.xchgs):
            label = QtGui.QLabel(type(x).__name__)
            label.setStyleSheet("QLabel { background-color : red; color : black; font-weight: bold; }")
            layout.addWidget(label, LABEL_ROW, i)

            bids_book = QtGui.QListWidget()
            bids_book.setMinimumHeight(200)
            layout.addWidget(bids_book, BIDS_BOOK_ROW, i)

            asks_book = QtGui.QListWidget()
            asks_book.setMinimumHeight(200)
            layout.addWidget(asks_book, ASKS_BOOK_ROW, i)

            trades = QtGui.QListWidget()
            trades.setMinimumHeight(200)
            layout.addWidget(trades, TRADES_ROW, i)

        plot = pg.PlotWidget()
        plot.setMinimumHeight(400)
        #plot.addLegend()
        layout.addWidget(plot, PRICE_CHART_ROW, 0, 1, len(self.xchgs))

    def refresh_orders_book(self, wgt: QtGui.QWidget, x: BaseX, side: str):
        orders = x.get_orders(side=side, limit=20, round=1)
        wgt.clear()
        wgt.insertItems(0, [f"{str(round(o[1], 2)):<7} {str(o[0])}" for o in orders])
        if side == "buy":
            wgt.scrollToTop()
        else:
            wgt.scrollToBottom()

    def refresh_trades(self, wgt, x):
        if x.trades_cnt == 0:
            return
        wgt.insertItems(0, [str(m) for m in list(x.trades)[:x.trades_cnt]])
        x.trades_cnt = 0
        #wgt.scrollToTop()

    def refresh_prices_chart(self, wgt):
        wgt.clear()
        legend = wgt.plotItem.legend

        for i, x in enumerate(self.xchgs):
            l = len(x.trades)
            if l == 0:
                continue
            #legend.removeItem(type(x).__name__)
            wgt.plot([t.time for t in list(x.trades)], [t.price for t in list(x.trades)], pen=i, name=type(x).__name__)


    def refresh(self):
        for i, x in enumerate(self.xchgs):
            self.refresh_orders_book(self.layout.itemAtPosition(BIDS_BOOK_ROW, i).widget(), x, 'buy')
            self.refresh_orders_book(self.layout.itemAtPosition(ASKS_BOOK_ROW, i).widget(), x, 'sell')
            self.refresh_trades(self.layout.itemAtPosition(TRADES_ROW, i).widget(), x)

        self.refresh_prices_chart(self.layout.itemAtPosition(PRICE_CHART_ROW, 0).widget())
