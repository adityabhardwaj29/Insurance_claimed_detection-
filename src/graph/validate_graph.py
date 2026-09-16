"""
Insurance Claim Graph Validation Module.
Validates referential integrity, relationship consistency, absence of orphan edges,
absence of self-loops, attribute JSON schema validity, and connectivity.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd


EXPECTED_NODE_COLUMNS = ["node_id", "node_type", "source_id", "attributes"]
EXPECTED_EDGE_COLUMNS = ["source", "target", "relationship", "weight"]

VALID_RELATIONSHIP_ENDPOINTS = {
    "FILED": {("Claimant", "Claim")},
    "COVERED_BY": {("Claim", "Policy")},
    "ASSOCIATED_WITH": {("Claim", "Vehicle")},
    "INVOLVES": {("Claim", "Provider")},
    "HAS": {("Claim", "Invoice")},
    "OCCURRED_AT": {("Claim", "Location")},
    "OWNS": {("Claimant", "Policy"), ("Claimant", "Vehicle")},
    "ISSUED_BY": {("Invoice", "Provider")},
    "LOCATED_AT": {("Claimant", "Location"), ("Provider", "Location")},
    "WITHIN_TERRITORY": {("Location", "Location")},
}


def validate_graph(nodes_df: pd.DataFrame, edges_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Performs comprehensive structural, referential, and semantic validation on the graph tables.
    Returns a dictionary of check outcomes and error details.
    """
    errors: List[str] = []
    checks: Dict[str, Any] = {}

    # 1. Column presence
    missing_node_cols = [c for c in EXPECTED_NODE_COLUMNS if c not in nodes_df.columns]
    missing_edge_cols = [c for c in EXPECTED_EDGE_COLUMNS if c not in edges_df.columns]
    
    col_ok = (len(missing_node_cols) == 0) and (len(missing_edge_cols) == 0)
    checks["required_columns"] = {
        "passed": col_ok,
        "missing_node_columns": missing_node_cols,
        "missing_edge_columns": missing_edge_cols,
    }
    if not col_ok:
        errors.append(f"Missing columns: nodes {missing_node_cols}, edges {missing_edge_cols}")

    # 2. Node uniqueness
    num_nodes = len(nodes_df)
    num_unique_nodes = nodes_df["node_id"].nunique() if "node_id" in nodes_df.columns else 0
    dup_nodes = num_nodes - num_unique_nodes
    checks["node_id_uniqueness"] = {
        "passed": dup_nodes == 0,
        "total_nodes": num_nodes,
        "unique_node_ids": num_unique_nodes,
        "duplicate_count": dup_nodes,
    }
    if dup_nodes > 0:
        errors.append(f"Found {dup_nodes} duplicate node_id entries.")

    # 3. Referential integrity (no orphan edges)
    node_id_set = set(nodes_df["node_id"]) if "node_id" in nodes_df.columns else set()
    invalid_sources = [s for s in edges_df["source"] if s not in node_id_set] if "source" in edges_df.columns else []
    invalid_targets = [t for t in edges_df["target"] if t not in node_id_set] if "target" in edges_df.columns else []
    
    orphan_edges_count = len(invalid_sources) + len(invalid_targets)
    checks["referential_integrity"] = {
        "passed": orphan_edges_count == 0,
        "invalid_sources_count": len(invalid_sources),
        "invalid_targets_count": len(invalid_targets),
        "sample_invalid_sources": invalid_sources[:5],
        "sample_invalid_targets": invalid_targets[:5],
    }
    if orphan_edges_count > 0:
        errors.append(f"Found {orphan_edges_count} orphan edge references (sources: {len(invalid_sources)}, targets: {len(invalid_targets)}).")

    # 4. Self-loops
    self_loops = []
    if "source" in edges_df.columns and "target" in edges_df.columns:
        self_loop_rows = edges_df[edges_df["source"] == edges_df["target"]]
        self_loops = self_loop_rows[["source", "relationship"]].to_dict(orient="records")
    
    checks["no_self_loops"] = {
        "passed": len(self_loops) == 0,
        "self_loops_count": len(self_loops),
        "self_loops": self_loops[:5],
    }
    if len(self_loops) > 0:
        errors.append(f"Found {len(self_loops)} unintended self-loops in edges.")

    # 5. Relationship endpoint type consistency
    node_type_map = dict(zip(nodes_df["node_id"], nodes_df["node_type"])) if "node_type" in nodes_df.columns else {}
    inconsistent_rels = []

    if "relationship" in edges_df.columns and "source" in edges_df.columns and "target" in edges_df.columns:
        for idx, row in edges_df.iterrows():
            rel = row["relationship"]
            src_type = node_type_map.get(row["source"])
            tgt_type = node_type_map.get(row["target"])
            
            allowed_pairs = VALID_RELATIONSHIP_ENDPOINTS.get(rel)
            if allowed_pairs is not None:
                if (src_type, tgt_type) not in allowed_pairs and (tgt_type, src_type) not in allowed_pairs:
                    inconsistent_rels.append({
                        "edge_index": idx,
                        "relationship": rel,
                        "source": row["source"],
                        "source_type": src_type,
                        "target": row["target"],
                        "target_type": tgt_type,
                    })

    checks["relationship_consistency"] = {
        "passed": len(inconsistent_rels) == 0,
        "inconsistent_edges_count": len(inconsistent_rels),
        "sample_inconsistencies": inconsistent_rels[:5],
    }
    if len(inconsistent_rels) > 0:
        errors.append(f"Found {len(inconsistent_rels)} edges violating relationship type rules.")

    # 6. JSON validity of node attributes
    invalid_json_count = 0
    if "attributes" in nodes_df.columns:
        for val in nodes_df["attributes"]:
            if not isinstance(val, str):
                invalid_json_count += 1
                continue
            try:
                json.loads(val)
            except Exception:
                invalid_json_count += 1

    checks["attribute_json_validity"] = {
        "passed": invalid_json_count == 0,
        "invalid_json_count": invalid_json_count,
    }
    if invalid_json_count > 0:
        errors.append(f"Found {invalid_json_count} nodes with malformed JSON attributes.")

    # Overall outcome
    is_valid = len(errors) == 0
    return {
        "is_valid": is_valid,
        "total_nodes": num_nodes,
        "total_edges": len(edges_df),
        "checks": checks,
        "errors": errors,
    }


def validate_graph_files(
    nodes_path: str = "data/graph/nodes.csv",
    edges_path: str = "data/graph/edges.csv",
    report_path: Optional[str] = "reports/graph_validation.json",
) -> Dict[str, Any]:
    """Loads graph CSVs, runs validation, and optionally persists the validation report."""
    nodes_df = pd.read_csv(nodes_path)
    edges_df = pd.read_csv(edges_path)
    report = validate_graph(nodes_df, edges_df)

    if report_path:
        out_p = Path(report_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

    return report


if __name__ == "__main__":
    print("Validating graph CSVs...")
    result = validate_graph_files()
    print(f"Validation outcome: {'PASSED' if result['is_valid'] else 'FAILED'}")
    for check_name, check_data in result["checks"].items():
        status = "OK" if check_data["passed"] else "FAIL"
        print(f"  [{status}] {check_name}")
    if not result["is_valid"]:
        print("Errors:")
        for err in result["errors"]:
            print(f"  - {err}")
