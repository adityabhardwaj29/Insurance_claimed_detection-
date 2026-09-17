"""
Phase 7: Graph Feature Engineering for Insurance Claim Fraud Detection.

Computes per-claim structural features from the heterogeneous insurance knowledge graph
built in Phase 6. All features are derived deterministically from graph topology;
no random numbers are used.

Features computed per claim:
  claim_degree            - degree of the claim node itself
  claimant_degree         - degree of the linked claimant node
  policy_degree           - degree of the linked policy node
  vehicle_degree          - degree of the linked vehicle node
  provider_degree         - degree of the linked provider node
  invoice_degree          - degree of the linked invoice node
  location_degree         - degree of the territory location node for this claim's claimant
  claim_pagerank          - PageRank score of the claim node
  claimant_pagerank       - PageRank score of the claimant node
  provider_pagerank       - PageRank score of the provider node
  claim_betweenness       - betweenness centrality of the claim node (approximated k=200)
  claimant_betweenness    - betweenness centrality of the claimant node
  provider_betweenness    - betweenness centrality of the provider node
  claim_clustering        - local clustering coefficient of the claim node
  claimant_clustering     - local clustering coefficient of the claimant node
  common_neighbors        - number of common neighbors between claimant and provider
  provider_claim_count    - number of INVOLVES edges from provider (raw count from edges)
  claimant_claim_count    - number of FILED edges from claimant (raw count from edges)
  repeated_claimant_provider - 1 if claimant and provider have been in more than 1 claim together
  fraud_neighbor_count    - count of connected claim nodes with fraud_label=1
  fraud_neighbor_ratio    - ratio of fraud neighbors to total claim neighbors
  suspicious_neighbor_count - count of neighbors whose node type is Provider AND appear in >10 claims
"""

import json
from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd
import networkx as nx

from src.graph.build_graph import build_insurance_graph


def compute_graph_features(
    relational_dir: str = "data/relational",
    graph_dir: str = "data/graph",
    output_path: Optional[str] = "data/features/graph_features.csv",
    pagerank_alpha: float = 0.85,
    betweenness_k: int = 200,
    betweenness_seed: int = 42,
) -> pd.DataFrame:
    """
    Computes per-claim graph features from the Phase 6 insurance knowledge graph.
    All features are topology-derived; no random imputation.
    """
    rel_path = Path(relational_dir)
    graph_path = Path(graph_dir)

    # Load relational tables
    claims = pd.read_csv(rel_path / "claims.csv")
    claimants = pd.read_csv(rel_path / "claimants.csv")

    # Build or load graph
    nodes_df, edges_df, G = build_insurance_graph(
        relational_dir=relational_dir,
        output_dir=None  # Don't re-export CSVs here
    )

    print(f"Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    # --- Pre-compute Global Graph Metrics ---

    print("Computing PageRank...")
    pagerank = nx.pagerank(G, alpha=pagerank_alpha)

    print(f"Computing betweenness centrality (k={betweenness_k})...")
    betweenness = nx.betweenness_centrality(
        G, k=betweenness_k, normalized=True, seed=betweenness_seed
    )

    print("Computing clustering coefficients...")
    clustering = nx.clustering(G)

    # --- Pre-compute Claim->Fraud maps ---
    fraud_label_map = dict(zip(
        "claim:" + claims["claim_id"],
        claims["fraud_label"].astype(int)
    ))

    # Pre-compute claimant -> all their claim nodes (for sibling-claim fraud features)
    claimant_to_claims: dict = {}
    for _, r in claims.iterrows():
        clt_key = f"claimant:{str(r['claimant_id'])}"
        clm_key = f"claim:{str(r['claim_id'])}"
        claimant_to_claims.setdefault(clt_key, []).append(clm_key)

    # Pre-compute provider -> all their claim nodes (for provider-level fraud patterns)
    provider_to_claims: dict = {}
    for _, r in claims.iterrows():
        prv_key = f"provider:{str(r['provider_id'])}"
        clm_key = f"claim:{str(r['claim_id'])}"
        provider_to_claims.setdefault(prv_key, []).append(clm_key)

    # Provider -> claim count (how many INVOLVES edges)
    provider_claim_count_map = (
        edges_df[edges_df["relationship"] == "INVOLVES"]
        .groupby("target")
        .size()
        .to_dict()
    )

    # Claimant -> claim count (how many FILED edges)
    claimant_claim_count_map = (
        edges_df[edges_df["relationship"] == "FILED"]
        .groupby("source")
        .size()
        .to_dict()
    )

    # Suspicious providers: those with above-median claim volume
    import statistics as _stats
    _prv_volumes = list(provider_claim_count_map.values())
    _median_volume = _stats.median(_prv_volumes) if _prv_volumes else 0
    suspicious_providers: set = {
        prv for prv, cnt in provider_claim_count_map.items() if cnt > _median_volume
    }

    # Repeated claimant-provider pair counts
    # For each (claimant, provider) pair, count claims involving both
    claimant_col = edges_df[edges_df["relationship"] == "FILED"].rename(
        columns={"source": "claimant_node", "target": "claim_node"}
    )[["claimant_node", "claim_node"]]

    provider_col = edges_df[edges_df["relationship"] == "INVOLVES"].rename(
        columns={"source": "claim_node", "target": "provider_node"}
    )[["claim_node", "provider_node"]]

    claimant_provider_pairs = (
        claimant_col
        .merge(provider_col, on="claim_node")
        .groupby(["claimant_node", "provider_node"])
        .size()
        .reset_index(name="pair_count")
    )
    repeated_pair_set = set(
        zip(
            claimant_provider_pairs[claimant_provider_pairs["pair_count"] > 1]["claimant_node"],
            claimant_provider_pairs[claimant_provider_pairs["pair_count"] > 1]["provider_node"],
        )
    )

    # Suspicious providers: those appearing in >10 claims
    SUSPICIOUS_PROVIDER_THRESHOLD = 10
    suspicious_providers = {
        node
        for node, count in provider_claim_count_map.items()
        if count > SUSPICIOUS_PROVIDER_THRESHOLD
    }

    # Claimant city map for location nodes
    claimant_city_map = dict(
        zip(claimants["claimant_id"].astype(str), claimants["city"].str.lower())
    )

    # --- Compute Per-Claim Features ---
    print("Computing per-claim features...")
    records = []

    for _, claim in claims.iterrows():
        cid = str(claim["claim_id"])
        clt_id = str(claim["claimant_id"])
        pol_id = str(claim["policy_id"])
        veh_id = str(claim["vehicle_id"])
        prv_id = str(claim["provider_id"])
        inv_id = str(claim["invoice_id"])

        clm_node = f"claim:{cid}"
        clt_node = f"claimant:{clt_id}"
        pol_node = f"policy:{pol_id}"
        veh_node = f"vehicle:{veh_id}"
        prv_node = f"provider:{prv_id}"
        inv_node = f"invoice:{inv_id}"

        # Location territory node
        city = claimant_city_map.get(clt_id)
        loc_node = f"location:{city}" if city else None

        def safe_degree(node):
            return G.degree(node) if node in G else 0

        def safe_pr(node):
            return pagerank.get(node, 0.0)

        def safe_bc(node):
            return betweenness.get(node, 0.0)

        def safe_cc(node):
            return clustering.get(node, 0.0)

        # Node degrees
        claim_degree = safe_degree(clm_node)
        claimant_degree = safe_degree(clt_node)
        policy_degree = safe_degree(pol_node)
        vehicle_degree = safe_degree(veh_node)
        provider_degree = safe_degree(prv_node)
        invoice_degree = safe_degree(inv_node)
        location_degree = safe_degree(loc_node) if loc_node else 0

        # PageRank
        claim_pagerank = safe_pr(clm_node)
        claimant_pagerank = safe_pr(clt_node)
        provider_pagerank = safe_pr(prv_node)

        # Betweenness centrality
        claim_betweenness = safe_bc(clm_node)
        claimant_betweenness = safe_bc(clt_node)
        provider_betweenness = safe_bc(prv_node)

        # Clustering coefficient
        claim_clustering = safe_cc(clm_node)
        claimant_clustering = safe_cc(clt_node)

        # Common neighbors between claimant and provider
        if clt_node in G and prv_node in G:
            clt_nbrs = set(G.neighbors(clt_node))
            prv_nbrs = set(G.neighbors(prv_node))
            common_neighbors = len(clt_nbrs & prv_nbrs)
        else:
            common_neighbors = 0

        # Provider and claimant claim volume
        prov_claim_count = provider_claim_count_map.get(prv_node, 0)
        clt_claim_count = claimant_claim_count_map.get(clt_node, 0)

        # Repeated claimant-provider relationship
        repeated_claimant_provider = int(
            (clt_node, prv_node) in repeated_pair_set
        )

        # Fraud neighbor features:
        # Count sibling claims filed by same claimant that are fraudulent (2-hop: claimant->claims)
        sibling_claims = [
            sib for sib in claimant_to_claims.get(clt_node, [])
            if sib != clm_node
        ]
        fraud_neighbor_count = sum(
            fraud_label_map.get(sib, 0) for sib in sibling_claims
        )
        total_siblings = len(sibling_claims)
        fraud_neighbor_ratio = (
            fraud_neighbor_count / total_siblings
            if total_siblings > 0 else 0.0
        )

        # Suspicious neighbor count:
        # Count how many of the claimant's other claims involved a suspicious (high-volume) provider
        suspicious_neighbor_count = 0
        for sib in claimant_to_claims.get(clt_node, []):
            # Get the provider for each sibling claim from claims dataframe
            sib_claim_id = sib.replace("claim:", "")
            sib_row = claims[claims["claim_id"] == sib_claim_id]
            if not sib_row.empty:
                sib_prv = f"provider:{sib_row.iloc[0]['provider_id']}"
                if sib_prv in suspicious_providers and sib_prv != prv_node:
                    suspicious_neighbor_count += 1

        records.append({
            "claim_id": cid,
            "claim_degree": claim_degree,
            "claimant_degree": claimant_degree,
            "policy_degree": policy_degree,
            "vehicle_degree": vehicle_degree,
            "provider_degree": provider_degree,
            "invoice_degree": invoice_degree,
            "location_degree": location_degree,
            "claim_pagerank": round(claim_pagerank, 8),
            "claimant_pagerank": round(claimant_pagerank, 8),
            "provider_pagerank": round(provider_pagerank, 8),
            "claim_betweenness": round(claim_betweenness, 8),
            "claimant_betweenness": round(claimant_betweenness, 8),
            "provider_betweenness": round(provider_betweenness, 8),
            "claim_clustering": round(claim_clustering, 8),
            "claimant_clustering": round(claimant_clustering, 8),
            "common_neighbors": common_neighbors,
            "provider_claim_count": prov_claim_count,
            "claimant_claim_count": clt_claim_count,
            "repeated_claimant_provider": repeated_claimant_provider,
            "fraud_neighbor_count": fraud_neighbor_count,
            "fraud_neighbor_ratio": round(fraud_neighbor_ratio, 6),
            "suspicious_neighbor_count": suspicious_neighbor_count,
        })

    df = pd.DataFrame(records)

    if output_path:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_p, index=False)
        print(f"Graph features saved: {out_p} ({len(df)} rows, {len(df.columns)} cols)")

    return df


if __name__ == "__main__":
    print("=== Phase 7: Computing Graph Features ===")
    df = compute_graph_features()
    print("\nFeature summary:")
    print(df.describe().round(4))
    print("\nFeature columns:", df.columns.tolist())
