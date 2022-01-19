# Copyright 2021 John Harwell, All rights reserved.
#
#  This file is part of SIERRA.
#
#  SIERRA is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  SIERRA is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  SIERRA.  If not, see <http://www.gnu.org/licenses/

# Core packages

# 3rd party packages
import networkx as nx
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
mpl.style.use('seaborn-colorblind')
# Project packages


def draw(G, pos, measures, measure_name, vmin: float, vmax: float, zaxis: bool):
    nodes = nx.draw_networkx_nodes(G, pos, node_size=10000, cmap=plt.cm.coolwarm,
                                   node_color=list(measures.values()),
                                   nodelist=measures.keys(),
                                   vmin=vmin,
                                   vmax=vmax)
    # nodes.set_norm(mcolors.SymLogNorm(linthresh=0.01, linscale=1, base=10))
    labels = nx.draw_networkx_labels(G, pos, font_size=24, font_color='k')
    edges = nx.draw_networkx_edges(G, pos)

    plt.title(measure_name, fontsize=28)

    if zaxis:
        bar = plt.colorbar(nodes)
        bar.ax.set_ylabel("Cross-Clique Centrality", fontsize=18)
        # bar.set_ticks([])

    # plt.axis('off')
    axis = plt.gca()
    axis.set_xlim([x*1.4 for x in axis.get_xlim()])
    axis.set_ylim([y*1.4 for y in axis.get_ylim()])
    # plt.tight_layout()
    # plt.show()


G0 = nx.Graph()
G0.add_node('Forage')

G1 = nx.Graph()
G1.add_node('Forage')
G1.add_node('Harvest')
G1.add_node('Collect')

# Decomposition edges
G1.add_edge('Forage', 'Harvest')
G1.add_edge('Forage', 'Collect')
G1.add_edge('Harvest', 'Collect')

G2 = nx.Graph()
G2.add_node('Forage')
G2.add_node('Harvest')
G2.add_node('Collect')
G2.add_node('Cache\nStart')
G2.add_node('Cache\nFinish')
G2.add_node('Cache\nTransfer')
G2.add_node('Cache\nCollect')

# Decomposition edges
G2.add_edge('Forage', 'Harvest')
G2.add_edge('Forage', 'Collect')
G2.add_edge('Harvest', 'Cache\nStart')
G2.add_edge('Harvest', 'Cache\nFinish')
G2.add_edge('Collect', 'Cache\nTransfer')
G2.add_edge('Collect', 'Cache\nCollect')

# Dependency edges
G2.add_edge('Harvest', 'Collect')
G2.add_edge('Cache\nStart', 'Cache\nFinish')
G2.add_edge('Cache\nFinish', 'Cache\nTransfer')
G2.add_edge('Cache\nTransfer', 'Cache\nCollect')
pos0 = nx.spring_layout(G0)
pos1 = nx.spring_layout(G1)
pos2 = nx.spring_layout(G2)

fig, ax = plt.subplots(ncols=3, figsize=(25, 10), gridspec_kw={'width_ratios':
                                                               [1.5, 2, 3]})

graphs = [G0, G1, G2]
positions = [pos0, pos1, pos2]
titles = ['No Caches\n(No Decomposition)',
          'Static Caches\n(Single Decomposition)',
          'Dynamic Caches\n(Multiple Decompositions)']
measures = [{'Forage': 1},
            {'Forage': 1,
             'Harvest': 1,
             'Collect': 1},
            {'Forage': 1,
             'Harvest': 2,
             'Collect': 2,
             'Cache\nStart': 1,
             'Cache\nFinish': 1,
             'Cache\nTransfer': 1,
             'Cache\nCollect': 1}]

for i in range(0, 3):
    plt.sca(ax[i])
    draw(graphs[i],
         positions[i],
         measures[i],
         titles[i],
         vmin=1,
         vmax=2,
         zaxis=(i == 2))

fig = plt.gcf()
fig.savefig("crossclioue_centrality.png", bbox_inches='tight')
# plt.show()
