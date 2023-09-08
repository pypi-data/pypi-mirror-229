
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.colors as colors
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt

import networkx as nx
import numpy as np
import functools


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


def visualize_graph(graph):
    
    # piviot the dictionary
    time_keys = set((t for _, edges in graph.items() for t in edges.keys()))
    n_steps = len(time_keys)
    dynamic_connections = {}
    for ts in time_keys:
        dynamic_connections.setdefault(ts, {})
        for n in graph:
            if ts in graph[n]: 
                dynamic_connections[ts][n] = graph[n][ts]

    # position for layout (mnetwork x)
    G = nx.DiGraph()

    for st in dynamic_connections.values():
        for s, ts in st.items(): 
            G.add_node(s)
            for t in ts:
                G.add_node(t)
                G.add_edge(s, t)

    pos = nx.spring_layout(G)
    nx.set_node_attributes(G, pos, 'pos')



    node_size = 26
    sc = 0.00
    traces = []



    # edges traces
    colorscale = 'Bluered'  # Choose the colorscale
    color_vals = np.array(list(time_keys))
    generated_colors = colors.sample_colorscale(colorscale, color_vals/np.linalg.norm(color_vals))
    generated_colors.reverse()


    for c, (ts, from_to) in zip(generated_colors, dynamic_connections.items()):
        # all edges for a given time
        edges = [(n0, n1) for n0 in from_to for n1 in from_to[n0]]

        edge_y, edge_z, edge_x = [], [], []
        for edge in edges:
            y0, z0 = G.nodes[edge[0]]['pos']
            y1, z1 = G.nodes[edge[1]]['pos']

            dy = y1 - y0
            dz = z1 - z0
            n = (dy**2 + dz**2 + ts**2)**0.5
            dy/=n
            dz/=n
            dx=ts/n

            edge_y += [y0+sc*dy, y1-sc*dy, None]
            edge_z += [z0+sc*dz, z1-sc*dz, None]
            edge_x += [0+sc*dx, ts-sc*dx, None]

        edge_y = np.array(edge_y)
        edge_z = np.array(edge_z)
        edge_x = np.array(edge_x)

        edge_trace = go.Scatter3d(
            x=edge_x,
            y=edge_y, z=edge_z,
            line=dict(width=6, color=c),
            hoverinfo='none',
            mode="markers+lines",
            marker=dict(
                color=c,
                size=0, 
            ),
            name=f'   t={ts}',
            legendgroup=f't={ts}',
            opacity=0.5
        )


        cone_x = edge_x[1::3]
        cone_y = edge_y[1::3]
        cone_z = edge_z[1::3]
        cone_u = cone_x - edge_x[:-1:3]
        cone_v = cone_y - edge_y[:-1:3]
        cone_w = cone_z - edge_z[:-1:3]
        norms = (cone_u**2 + cone_v**2 + cone_w**2)**0.5
        cone_u /= norms
        cone_v /= norms
        cone_w /= norms
        
        recover_scale = np.inf
        for i, (x, y, z) in enumerate(zip(cone_x, cone_y, cone_z)):
            p1 = np.array([x, y, z])
            if i:
                recover_scale = min(recover_scale, np.sqrt(np.sum((p1-p2)**2)))
                print(ts, np.sqrt(np.sum((p1-p2)**2)))
            p2 = np.array(p1)
            
        if recover_scale == np.inf:
            recover_scale = 1.0
            
        print(recover_scale)

        if ts!= 0:
            lg = f't={ts}'

        cone_trace = go.Cone(
            x=cone_x,  
            y=cone_y,  
            z=cone_z,  
            u=cone_u, 
            v=cone_v,
            w=cone_w,
            colorscale=[[0, c], [1, c]],
            sizeref=0.1/recover_scale, 
            anchor="tip",
            showscale=False,
            legendgroup=f't={ts}',
            opacity=0.5,
            hoverinfo=None,
            sizemode='scaled'
        )

        if ts != 0:
            edge_trace.visible = 'legendonly'
            cone_trace.visible = 'legendonly'

        traces.append(edge_trace)  
        traces.append(cone_trace)



    # # node traces
    # node_y = []
    # node_z = []
    # labels = []
    # for node in G.nodes():
    #     y, z = G.nodes[node]['pos']
    #     labels.append(node)
    #     node_y.append(y)
    #     node_z.append(z)


    colorscale = 'Hot'  # Choose the colorscale
    color_vals = np.array(list(time_keys))
    generated_colors = colors.sample_colorscale(colorscale, color_vals/np.linalg.norm(color_vals))

    for i, x in enumerate(list(time_keys)):
        lg = f't={x}' if x!=0 else None
        if x == 0:
            nodes = G.nodes()
        else:
            cur_dict = dynamic_connections[x]
            nodes = list(set(functools.reduce(lambda a, b : a+b, cur_dict.values())))
        node_y = []
        node_z = []
        labels = []
        for node in nodes:
            y, z = G.nodes[node]['pos']
            labels.append(node)
            node_y.append(y)
            node_z.append(z)
        node_trace = go.Scatter3d(
                x=[x]*len(node_y), 
                y=node_y,
                z=node_z, 
                opacity=0.6,
                text=np.tile(labels, n_steps),
                mode='markers+text',
                textfont=dict(
                    family="monospace",
                    size=16,
                    color='White'
                ),
                textposition='middle center',
                hoverinfo=None,
                marker=dict(
                    # colorscale options
                    #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
                    #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
                    #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
                    colorscale='YlGnBu',
                    color=generated_colors[i],
                    size=node_size
                    ),
                showlegend=False,
                legendgroup=lg
            )

        if x != 0:
            node_trace.visible = 'legendonly'
        traces.append(node_trace)


    # Add the cone trace to the list of traces
    padding = 0.2
    fig = go.Figure(data=traces,
                    layout=go.Layout(
                        height=600,
                        width=600,
                        hovermode='closest',
                        margin=dict(b=0,l=0,r=0,t=50),
                        annotations=[ dict(
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002 ) ],
                        scene=dict(aspectratio=dict(x=1.5, y=2, z=2),
                                   camera=dict(eye=dict(x=-3, y=0, z=0))  # Adjust the eye coordinates for desired iso view
                            )
                    ),

                    )
    for tr in fig.data:
        tr.hoverinfo = 'skip'

    if fig.data:
        y_min = min(fig.data[2*len(time_keys)].y) - padding
        y_max = max(fig.data[2*len(time_keys)].y) + padding
        z_min = min(fig.data[2*len(time_keys)].z) - padding
        z_max = max(fig.data[2*len(time_keys)].z) + padding
        fig.update_layout(scene=dict(
            yaxis=dict(range=[y_min, y_max], visible=False, showspikes=False),
            zaxis=dict(range=[z_min, z_max], visible=False, showspikes=False),
            xaxis=dict(range=[0, max(time_keys)+0.5], title='t', showspikes=False, showbackground=False)
        ))



    fig.show()





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