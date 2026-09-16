"""
Insurance Claim Graph Construction Module.
Builds the heterogeneous insurance knowledge and claim network graph from relational tables.

Entities (Nodes):
- Claim
- Claimant
- Policy
- Vehicle
- Provider
- Invoice
- Location (territory hubs and specific locations)

Relationships (Edges):
- Claimant -- OWNS --> Policy
- Claimant -- OWNS --> Vehicle
- Claimant -- FILED --> Claim
- Claimant -- LOCATED_AT --> Location
- Claim -- COVERED_BY --> Policy
- Claim -- ASSOCIATED_WITH --> Vehicle
- Claim -- INVOLVES --> Provider
- Claim -- HAS --> Invoice
- Claim -- OCCURRED_AT --> Location
- Invoice -- ISSUED_BY --> Provider
- Provider -- LOCATED_AT --> Location
- Location -- WITHIN_TERRITORY --> Location
"""

import os
import json
from pathlib import Path
from typing import Dict, Tuple, Optional, Any
import pandas as pd
import networkx as nx


def serialize_attributes(row: pd.Series, exclude_cols: list) -> str:
    """Serializes row attributes to a sorted JSON string, converting NaN to None."""
    attrs = {}
    for k, v in row.items():
        if k not in exclude_cols:
            if pd.isna(v):
                attrs[k] = None
            elif isinstance(v, (int, float, str, bool)):
                attrs[k] = v
            else:
                attrs[k] = str(v)
    return json.dumps(attrs, sort_keys=True)


def extract_nodes(tables: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Extracts all distinct nodes from relational tables with schema:
    [node_id, node_type, source_id, attributes]
    """
    nodes = []

    claims = tables.get("claims", pd.DataFrame())
    claimants = tables.get("claimants", pd.DataFrame())
    policies = tables.get("policies", pd.DataFrame())
    vehicles = tables.get("vehicles", pd.DataFrame())
    providers = tables.get("providers", pd.DataFrame())
    invoices = tables.get("invoices", pd.DataFrame())
    locations = tables.get("locations", pd.DataFrame())

    # 1. Claim Nodes
    if not claims.empty:
        for _, r in claims.iterrows():
            cid = str(r["claim_id"])
            attrs = serialize_attributes(
                r, ["claim_id", "claimant_id", "policy_id", "vehicle_id", "provider_id", "invoice_id"]
            )
            nodes.append({
                "node_id": f"claim:{cid}",
                "node_type": "Claim",
                "source_id": cid,
                "attributes": attrs,
            })

    # 2. Claimant Nodes
    if not claimants.empty:
        for _, r in claimants.iterrows():
            cid = str(r["claimant_id"])
            attrs = serialize_attributes(r, ["claimant_id"])
            nodes.append({
                "node_id": f"claimant:{cid}",
                "node_type": "Claimant",
                "source_id": cid,
                "attributes": attrs,
            })

    # 3. Policy Nodes
    if not policies.empty:
        for _, r in policies.iterrows():
            pid = str(r["policy_id"])
            attrs = serialize_attributes(r, ["policy_id", "claimant_id"])
            nodes.append({
                "node_id": f"policy:{pid}",
                "node_type": "Policy",
                "source_id": pid,
                "attributes": attrs,
            })

    # 4. Vehicle Nodes
    if not vehicles.empty:
        for _, r in vehicles.iterrows():
            vid = str(r["vehicle_id"])
            attrs = serialize_attributes(r, ["vehicle_id", "claimant_id"])
            nodes.append({
                "node_id": f"vehicle:{vid}",
                "node_type": "Vehicle",
                "source_id": vid,
                "attributes": attrs,
            })

    # 5. Provider Nodes
    if not providers.empty:
        for _, r in providers.iterrows():
            prv_id = str(r["provider_id"])
            attrs = serialize_attributes(r, ["provider_id"])
            nodes.append({
                "node_id": f"provider:{prv_id}",
                "node_type": "Provider",
                "source_id": prv_id,
                "attributes": attrs,
            })

    # 6. Invoice Nodes
    if not invoices.empty:
        for _, r in invoices.iterrows():
            inv_id = str(r["invoice_id"])
            attrs = serialize_attributes(r, ["invoice_id", "provider_id"])
            nodes.append({
                "node_id": f"invoice:{inv_id}",
                "node_type": "Invoice",
                "source_id": inv_id,
                "attributes": attrs,
            })

    # 7. Location Nodes (Territory hubs + Specific location pins)
    city_set = set()
    if not claimants.empty and "city" in claimants.columns:
        city_set.update(claimants["city"].dropna().unique())
    if not providers.empty and "city" in providers.columns:
        city_set.update(providers["city"].dropna().unique())
    if not locations.empty and "city" in locations.columns:
        city_set.update(locations["city"].dropna().unique())

    for city in sorted(list(city_set)):
        city_slug = str(city).strip().lower()
        nodes.append({
            "node_id": f"location:{city_slug}",
            "node_type": "Location",
            "source_id": str(city),
            "attributes": json.dumps({"city": str(city), "level": "territory_hub"}, sort_keys=True),
        })

    if not locations.empty:
        for _, r in locations.iterrows():
            lid = str(r["location_id"])
            lid_slug = lid.strip().lower()
            attrs = serialize_attributes(r, ["location_id"])
            nodes.append({
                "node_id": f"location:{lid_slug}",
                "node_type": "Location",
                "source_id": lid,
                "attributes": attrs,
            })

    df = pd.DataFrame(nodes)
    # Ensure uniqueness of node_id
    df = df.drop_duplicates(subset=["node_id"]).reset_index(drop=True)
    return df


def extract_edges(tables: Dict[str, pd.DataFrame], valid_node_ids: Optional[set] = None) -> pd.DataFrame:
    """
    Extracts all edges from relational tables with schema:
    [source, target, relationship, weight]
    """
    edges = []

    claims = tables.get("claims", pd.DataFrame())
    claimants = tables.get("claimants", pd.DataFrame())
    policies = tables.get("policies", pd.DataFrame())
    vehicles = tables.get("vehicles", pd.DataFrame())
    providers = tables.get("providers", pd.DataFrame())
    invoices = tables.get("invoices", pd.DataFrame())
    locations = tables.get("locations", pd.DataFrame())

    # 1. Specific Location -> Territory Hub: WITHIN_TERRITORY
    if not locations.empty:
        for _, r in locations.iterrows():
            lid = str(r["location_id"]).strip().lower()
            city = str(r["city"]).strip().lower()
            edges.append({
                "source": f"location:{lid}",
                "target": f"location:{city}",
                "relationship": "WITHIN_TERRITORY",
                "weight": 1.0,
            })

    # 2. Claimant -> Policy: OWNS
    if not policies.empty:
        for _, r in policies.iterrows():
            clt = str(r["claimant_id"])
            pol = str(r["policy_id"])
            edges.append({
                "source": f"claimant:{clt}",
                "target": f"policy:{pol}",
                "relationship": "OWNS",
                "weight": 1.0,
            })

    # 3. Claimant -> Vehicle: OWNS
    if not vehicles.empty:
        for _, r in vehicles.iterrows():
            clt = str(r["claimant_id"])
            veh = str(r["vehicle_id"])
            edges.append({
                "source": f"claimant:{clt}",
                "target": f"vehicle:{veh}",
                "relationship": "OWNS",
                "weight": 1.0,
            })

    # 4. Claimant -> Location: LOCATED_AT
    if not claimants.empty:
        for _, r in claimants.iterrows():
            clt = str(r["claimant_id"])
            if pd.notna(r.get("city")):
                city = str(r["city"]).strip().lower()
                edges.append({
                    "source": f"claimant:{clt}",
                    "target": f"location:{city}",
                    "relationship": "LOCATED_AT",
                    "weight": 1.0,
                })

    # 5. Provider -> Location: LOCATED_AT
    if not providers.empty:
        for _, r in providers.iterrows():
            prv = str(r["provider_id"])
            if pd.notna(r.get("city")):
                city = str(r["city"]).strip().lower()
                edges.append({
                    "source": f"provider:{prv}",
                    "target": f"location:{city}",
                    "relationship": "LOCATED_AT",
                    "weight": 1.0,
                })

    # 6. Invoice -> Provider: ISSUED_BY
    if not invoices.empty:
        for _, r in invoices.iterrows():
            inv = str(r["invoice_id"])
            prv = str(r["provider_id"])
            edges.append({
                "source": f"invoice:{inv}",
                "target": f"provider:{prv}",
                "relationship": "ISSUED_BY",
                "weight": 1.0,
            })

    # 7. Claim-centric relationships
    claimant_city_map = {}
    if not claimants.empty:
        claimant_city_map = dict(zip(claimants["claimant_id"].astype(str), claimants["city"].astype(str)))

    if not claims.empty:
        for _, r in claims.iterrows():
            cid = f"claim:{str(r['claim_id'])}"
            clt_id = str(r["claimant_id"])
            pol_id = str(r["policy_id"])
            veh_id = str(r["vehicle_id"])
            prv_id = str(r["provider_id"])
            inv_id = str(r["invoice_id"])

            # Claimant -- FILED --> Claim
            edges.append({
                "source": f"claimant:{clt_id}",
                "target": cid,
                "relationship": "FILED",
                "weight": 1.0,
            })

            # Claim -- COVERED_BY --> Policy
            edges.append({
                "source": cid,
                "target": f"policy:{pol_id}",
                "relationship": "COVERED_BY",
                "weight": 1.0,
            })

            # Claim -- ASSOCIATED_WITH --> Vehicle
            edges.append({
                "source": cid,
                "target": f"vehicle:{veh_id}",
                "relationship": "ASSOCIATED_WITH",
                "weight": 1.0,
            })

            # Claim -- INVOLVES --> Provider
            edges.append({
                "source": cid,
                "target": f"provider:{prv_id}",
                "relationship": "INVOLVES",
                "weight": 1.0,
            })

            # Claim -- HAS --> Invoice
            edges.append({
                "source": cid,
                "target": f"invoice:{inv_id}",
                "relationship": "HAS",
                "weight": 1.0,
            })

            # Claim -- OCCURRED_AT --> Location (territory)
            city = claimant_city_map.get(clt_id)
            if city:
                city_slug = str(city).strip().lower()
                edges.append({
                    "source": cid,
                    "target": f"location:{city_slug}",
                    "relationship": "OCCURRED_AT",
                    "weight": 1.0,
                })

    df = pd.DataFrame(edges)

    # Filter by valid node ids if provided
    if valid_node_ids is not None:
        df = df[df["source"].isin(valid_node_ids) & df["target"].isin(valid_node_ids)].copy()

    # Drop duplicate edges with same source, target, relationship
    df = df.drop_duplicates(subset=["source", "target", "relationship"]).reset_index(drop=True)
    return df


def build_insurance_graph(
    relational_dir: str = "data/relational",
    output_dir: Optional[str] = "data/graph",
) -> Tuple[pd.DataFrame, pd.DataFrame, nx.Graph]:
    """
    Builds the insurance graph from relational CSV tables.
    Returns (nodes_df, edges_df, nx.Graph).
    If output_dir is provided, writes nodes.csv and edges.csv.
    """
    rel_path = Path(relational_dir)
    tables = {}
    table_names = ["claims", "claimants", "policies", "vehicles", "providers", "invoices", "locations"]

    for name in table_names:
        file_path = rel_path / f"{name}.csv"
        if file_path.exists():
            tables[name] = pd.read_csv(file_path)
        else:
            tables[name] = pd.DataFrame()

    nodes_df = extract_nodes(tables)
    valid_ids = set(nodes_df["node_id"])
    edges_df = extract_edges(tables, valid_node_ids=valid_ids)

    # Construct NetworkX Graph
    G = nx.Graph()
    for _, r in nodes_df.iterrows():
        try:
            attrs = json.loads(r["attributes"]) if isinstance(r["attributes"], str) else {}
        except Exception:
            attrs = {}
        G.add_node(
            r["node_id"],
            node_type=r["node_type"],
            source_id=r["source_id"],
            **attrs,
        )

    for _, r in edges_df.iterrows():
        G.add_edge(
            r["source"],
            r["target"],
            relationship=r["relationship"],
            weight=float(r["weight"]),
        )

    # Save outputs if output_dir specified
    if output_dir:
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        nodes_df.to_csv(out_path / "nodes.csv", index=False)
        edges_df.to_csv(out_path / "edges.csv", index=False)

    return nodes_df, edges_df, G


if __name__ == "__main__":
    print("Building insurance relationship graph...")
    nodes_df, edges_df, G = build_insurance_graph()
    print(f"Graph construction complete:")
    print(f"  Total nodes: {len(nodes_df)}")
    print(f"  Total edges: {len(edges_df)}")
    print(f"  Node types: {nodes_df['node_type'].value_counts().to_dict()}")
    print(f"  Relationships: {edges_df['relationship'].value_counts().to_dict()}")
    print(f"  NetworkX nodes: {G.number_of_nodes()}, edges: {G.number_of_edges()}")
    print(f"  Connected components: {nx.number_connected_components(G)}")
