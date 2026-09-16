import networkx as nx

def build_claim_graph(claims):
    G=nx.Graph()
    for _,r in claims.iterrows():
        claim=r["claim_id"]
        G.add_node(claim, node_type="claim")
        for col,typ in [("claimant_id","claimant"),("policy_id","policy"),
                        ("vehicle_id","vehicle"),("provider_id","provider"),("invoice_id","invoice")]:
            value=r.get(col)
            if value:
                G.add_node(value,node_type=typ)
                G.add_edge(claim,value,relation=typ)
    return G
