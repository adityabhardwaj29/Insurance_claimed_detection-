import networkx as nx
def extract_graph_features(G):
    degree=dict(G.degree())
    return {"degree":degree, "components":[len(c) for c in nx.connected_components(G)]}
