
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.colors as colors
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt

from yfiles_jupyter_graphs import GraphWidget
import networkx as nx
import numpy as np


def visualize_ts(df, fig_width=2000, fig_height=600):

    fig = make_subplots(rows=len(df.columns), cols=1, shared_xaxes=True, vertical_spacing=0.02)

    # y_range = [df.min().min(), df.max().max()]

    for i, column in enumerate(df.columns):
        fig.add_trace(go.Scatter(x=df.index, y=df[column], name=column, mode='lines'), row=i+1, col=1)
        fig.update_yaxes(title_text=column, row=i+1, col=1)

    fig.update_layout(
        width=fig_width, 
        height=fig_height, 
        margin=dict(l=40, r=10, t=10, b=10)  # Adjust these values as desired
    )
    fig.show()


def create_yf(graph):
    colorscale = 'Hot'  # Choose the colorscale
    color_vals = np.array(graph.lags)
    sampled_colors = colors.sample_colorscale(colorscale, color_vals/np.linalg.norm(color_vals))
    generated_colors = {lag: color for lag, color in zip(color_vals, sampled_colors)}
    

    nodes2id = {}
    yf_nodes = []
    for i, n in enumerate(graph.nodes):
        nodes2id[n] = i
        yf_nodes.append(dict(id=i, properties=dict(yf_label=n)))
        
    yf_edges = []
    for i, (u, v, lag) in enumerate(graph.edges(keys=True)):
        yf_edges.append(dict(id=i, start=nodes2id[u], end=nodes2id[v], properties=dict(lag=lag)))
        
    def e_color_mapping(index, element):
        return generated_colors[element['properties']['lag']]
    
    def n_color_mapping(index, element):
        return '#AAAAAA'
    
    def n_scale_mapping(index, element):
        return 0.5
    
    w = GraphWidget()
    w.set_nodes(yf_nodes)
    w.set_edge_color_mapping(e_color_mapping)
    w.set_node_color_mapping(n_color_mapping)
    w.set_node_scale_factor_mapping(n_scale_mapping)
    w.set_edges(yf_edges)
    w.directed = True
    return w




def visualize_nx(pgv, pos=None):
    if pos is None:
        pos = nx.spring_layout(pgv) 
    plt.figure()
    nx.draw(
        pgv, pos, edge_color='black', width=1, linewidths=1,
        node_size=800, node_color='pink', alpha=0.8,
        labels={node: node for node in pgv.nodes()}
    )
    nx.draw_networkx_edge_labels(
        pgv, pos, 
        edge_labels={(u, v): k for (u, v, k) in pgv.edges(keys=True)},
        font_color='red'
    )
    plt.axis('off')
    plt.show()
    return pos