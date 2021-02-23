"""Created by Michal Ociepa"""

import options
from src.binomial_tree import BinomialTree
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
from icecream import ic

pio.renderers.default = 'browser'


#############################

def create_strategic_matrix(analyzer):
    ksi_0, ksi_1 = analyzer.find_replicating_strategy()
    ksi_0 = np.vstack([ksi_0, np.repeat(np.nan, np.size(ksi_0, 1))])
    ksi_0 = np.c_[ksi_0, np.repeat(np.nan, np.size(ksi_0, 0))]
    ksi_1 = np.vstack([ksi_1, np.repeat(np.nan, np.size(ksi_1, 1))])
    ksi_1 = np.c_[ksi_1, np.repeat(np.nan, np.size(ksi_1, 0))]

    return ksi_0, ksi_1


def long_df(tree):
    z = [tree[:(t + 1), t] for t in range(tree.shape[0])]
    y = [np.array([i * np.ones_like(z[i]), z[i]]).T for i in range(len(z))]

    return pd.DataFrame(np.concatenate(y, axis=0), columns=['Time', 'Value'])


def create_dataframe(tree, analyzer, option=None, bermuda=None):
    ksi_0, ksi_1 = create_strategic_matrix(analyzer)
    df1 = long_df(tree.tree)
    df1.columns = ["Time", "Stock_Price"]  # stock price frame
    df2 = long_df(analyzer.payoff_tree)
    df2.columns = ["Time", "Payoff"]  # payoff frame
    df3 = long_df(analyzer.envelope_tree)
    df3.columns = ["Time", "Snell"]  # snell frame
    df4 = long_df(np.where(analyzer.envelope_tree == analyzer.payoff_tree, 1, 0))
    df4.Value = np.where(df4.Value == 1, "Yes", "No")
    if option == 'Bermuda':
        freq_seq = [t for t in range(bermuda, tree.tree.shape[1], bermuda)]
        if freq_seq[-1] != tree.tree.shape[1] - 1:
            freq_seq.append(tree.tree.shape[1] - 1)
        zeros_ids = np.delete(np.arange(tree.tree.shape[1]), freq_seq)
        df4.loc[df4.Time.apply(lambda x: x in zeros_ids), 'Value'] = 'Not Applicable'
    df4.columns = ["Time", "If_Stopping_Time"]  # stopping time frame
    df5 = long_df(ksi_0)
    df5.columns = ["Time", "ksi_0"]  # money frame
    df6 = long_df(ksi_1)
    df6.columns = ["Time", "ksi_1"]  # number of shares frame

    data = pd.concat([df1, df2, df3, df4, df5, df6], axis=1, join="inner")
    data = data.loc[:, ~data.columns.duplicated()]
    data['logarithm'] = np.log(data.Stock_Price)
    data['Difference'] = data.Snell - (data.Stock_Price * data.ksi_1 + data.ksi_0)

    return data


def plot_heatmap(data, parameter, title, label=None, if_logarithm=False):
    if label == None:
        label = parameter

    if if_logarithm:
        data["logParameter"] = np.log(data[parameter])
        parameter = "logParameter"

    fig = px.scatter(data, x='Time', y='logarithm', color=parameter,
                     color_continuous_scale="Viridis",
                     # color_discrete_sequence = ["grey", "red"],
                     title=title,
                     labels={parameter: label},
                     hover_data={'Time': True,  # remove species from hover data
                                 parameter: False,
                                 'logarithm': False,
                                 'Stock Price': (':.4f', data.Stock_Price),  # customize hover for column of y attribute
                                 'Snell Price': (':.4f', data.Snell),  # add other column, customized formatting
                                 'Number of Shares': (':.4f', data.ksi_1),
                                 'Money': (':.4f', data.ksi_0),
                                 'Stopping Time': data.If_Stopping_Time,  # add other column, default formatting
                                 'Difference Snell - Security': (':.4f', data.Difference)
                                 },
                     width=1000, height=500)
    fig.update_layout(margin=dict(l=100, r=100, b=100, t=100))

    fig.update_yaxes(showticklabels=False, visible=False)

    config = {
        'scrollZoom': False,
        'displayModeBar': True,
        'editable': False,
        'showLink': True,
        'displaylogo': True,
        'responsive': False,
        'toImageButtonOptions': {
            'format': 'png',  # one of png, svg, jpeg, webp
            'filename': 'custom_image',
            # 'height': 500,
            'width': 800,
            'scale': 1,  # Multiply title/legend/axis/canvas sizes by this factor
        }
    }
    return fig
