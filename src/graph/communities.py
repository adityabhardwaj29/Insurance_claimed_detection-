import networkx as nx
def communities(G):
    return list(nx.community.greedy_modularity_communities(G))
