# s = """
# select *
# from pubmed.paper any
#          inner join (select pm_id, datetime_str from pubmed.nft_paper) using pm_id
# group by;
# """
#
# match = re.match(r'from (\w+\.\w+)', s)
# print(match)
# match = re.findall('datetime_str from' + ' (\\w+\.\\w+)', s)
# print(match)
import matplotlib.pyplot as plt
import networkx as nx
# import pylab

G = nx.DiGraph()
# G.add_nodes_from(['A', 'B', 'C', 'D', 'E', 'F', 'G'])

G.add_edges_from([('A', 'B'), ('C', 'D'), ('G', 'D')], weight=1)
G.add_edges_from([('D', 'A'), ('D', 'E'), ('B', 'D'), ('D', 'E')], weight=2)
G.add_edges_from([('B', 'C'), ('E', 'F')], weight=3)
G.add_edges_from([('C', 'F')], weight=4)

# red_edges = [('C', 'D'), ('D', 'A')]
# edge_colors = ['black' if not edge in red_edges else 'red' for edge in G.edges()]

pos = nx.spring_layout(G)
# edge_labels = dict([((u, v,), d['weight']) for u, v, d in G.edges(data=True)])
# nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

# val_map = {'A': 1.0,
#            'D': 0.5714285714285714,
#            'H': 0.0}
# values = [val_map.get(node, 0.45) for node in G.nodes()]
print(list(nx.bfs_edges(G, 'B')))
nx.draw_networkx(G, pos, node_size=500, edge_cmap=plt.cm.Reds)  # ,node_color=values,  edge_color=edge_colors
plt.savefig('table-relations.png', format="PNG")
plt.show() # block = False


# import matplotlib.pyplot as plt
# import networkx as nx
#
# G = nx.DiGraph()  # 创建一个空的无向图
#
# num = 6
# nodes = list(range(num))  # [0,1,2,3,4,5]
# # 将节点添加到网络中
# G.add_nodes_from(nodes)  # 从列表中加点
#
# edges = []  # 存放所有的边，构成无向图（去掉最后一个结点，构成一个环）
# for idx in range(num - 1):
#     edges.append((idx, idx + 1))
# edges.append((num - 1, 0))
# G.add_edges_from(edges)
#
# nx.draw_networkx(G)
# plt.show()