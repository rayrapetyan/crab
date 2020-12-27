import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt

sym_conf = {
    'ETHUSD': {
        'min_price': 400,
        'max_price': 800,
        'price_step': 1,
    },
    'BTCUSD': {
        'min_price': 10000,
        'max_price': 30000,
        'price_step': 100,
    }

}


def heatmap(data, row_labels, col_labels, ax=None, cbar_kw={}, cbarlabel="", **kwargs):
    """
    Create a heatmap from a numpy array and two lists of labels.

    Parameters
    ----------
    data
        A 2D numpy array of shape (N, M).
    row_labels
        A list or array of length N with the labels for the rows.
    col_labels
        A list or array of length M with the labels for the columns.
    ax
        A `matplotlib.axes.Axes` instance to which the heatmap is plotted.  If
        not provided, use current axes or create a new one.  Optional.
    cbar_kw
        A dictionary with arguments to `matplotlib.Figure.colorbar`.  Optional.
    cbarlabel
        The label for the colorbar.  Optional.
    **kwargs
        All other arguments are forwarded to `imshow`.
    """

    if not ax:
        ax = plt.gca()

    ax.set_ylim(ax.get_ylim()[::1])

    # Plot the heatmap
    im = ax.imshow(data, **kwargs)

    # Create colorbar
    cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
    cbar.ax.set_ylabel(cbarlabel, rotation=90)

    # We want to show all ticks...
    ax.set_xticks(np.arange(data.shape[1]))
    ax.set_yticks(np.arange(data.shape[0]))

    # minor ticks should be set separately
    ax.set_xticks(np.arange(data.shape[1] + 1) - .5, minor=True)
    ax.set_yticks(np.arange(data.shape[0] + 1) - .5, minor=True)

    # ... and label them with the respective list entries.
    ax.set_xticklabels(col_labels)
    ax.set_yticklabels(row_labels)

    ax.tick_params(bottom=True, labelbottom=True, right=True, labelright=True,
                   left=False, labelleft=False, top=False, labeltop=False)

    ax.yaxis.set_label_position("right")
    ax.yaxis.set_ticks_position("right")

    plt.xlabel("Date/Time")
    plt.ylabel("Price [USD]")

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    plt.locator_params(axis='y', nbins=20)
    plt.locator_params(axis='x', nbins=5)

    return im, cbar


def gen_heatmap_data(values, xticks, yticks, y_min, y_max, y_step):
    res = np.zeros((yticks, xticks))
    for x, vals_block in enumerate(values):
        for vals in vals_block:
            y_raw = vals[0]
            if y_min <= y_raw < y_max:
                y = int((y_raw - y_min) / y_step)
                data = vals[0] * vals[1]
                res[y, x] += data
    return res


df_orders = pd.read_parquet('/ara/devel/sandbox/crab/data/orders_v1.parquet')
df_trades = pd.read_parquet('/ara/devel/sandbox/crab/data/trades_v1.parquet')
for sym in sym_conf.keys():
    df_trades_filtered = df_trades.query(f'sym == "{sym}" & xname != "foo"')
    pv = df_trades_filtered.groupby(['ts']).agg({
        'trades': 'sum',
    })['trades']
    pv = pd.DataFrame(pv.values.tolist()).mean(1)

    df_orders_filtered = df_orders.query(f'sym == "{sym}" & xname != "foo"')
    timestamps_raw = df_orders_filtered['ts'].unique().tolist()
    timestamps = []
    for ts in timestamps_raw:
        v = datetime.datetime.fromtimestamp(ts)
        timestamps.append(f"{v:%b %d %H:%M}")

    price_min = sym_conf[sym]['min_price']
    price_max = sym_conf[sym]['max_price']
    price_step = sym_conf[sym]['price_step']
    prices = np.arange(price_min, price_max, price_step).tolist()

    volumes = []
    ov = df_orders_filtered.groupby(['ts']).agg({
        'orders': 'sum',
    })['orders']
    volumes = gen_heatmap_data(
        ov,
        xticks=len(timestamps),
        yticks=len(prices),
        y_min=price_min,
        y_max=price_max,
        y_step=price_step
    )

    fig, ax = plt.subplots(figsize=(15, 10))

    im, cbar = heatmap(volumes, prices, timestamps, ax=ax, cmap="hot", cbarlabel=f"Volume [USD]",
                       cbar_kw={'orientation': 'vertical'})

    fig.tight_layout()

    # plot price
    prices_x = np.arange(len(timestamps))
    prices_y = [(x-price_min)/price_step for x in pv]
    plt.plot(prices_x, prices_y, linewidth=2)

    plt.show()
