from __future__ import annotations

import json
from datetime import datetime

import pandas as pd

from modules.data_gen import load_tables, write_table
from modules.guardrails import validate_cluster_constraints


def _now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _next_id(prefix: str, series: pd.Series) -> str:
    if series.empty:
        return f"{prefix}0001"
    nums = (
        series.astype(str)
        .str.extract(r"(\d+)", expand=False)
        .fillna("0")
        .astype(int)
    )
    return f"{prefix}{nums.max() + 1:04d}"


def load_override_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    tables = load_tables()
    return tables["override_requests"], tables["override_audit_log"]


def _write_audit(
    audit_df: pd.DataFrame,
    request_id: str,
    action: str,
    operator: str,
    diff_json: dict,
) -> pd.DataFrame:
    audit_id = _next_id("A", audit_df["audit_id"]) if not audit_df.empty else "A0001"
    row = {
        "audit_id": audit_id,
        "request_id": request_id,
        "action": action,
        "operator": operator,
        "timestamp": _now_str(),
        "diff_json": json.dumps(diff_json, ensure_ascii=True),
    }
    return pd.concat([audit_df, pd.DataFrame([row])], ignore_index=True)


def submit_override(
    store_id: str,
    cluster_id: str,
    sku_id: str,
    field_to_override: str,
    old_value: str,
    new_value: str,
    requester: str,
    reason_text: str,
) -> str:
    requests, audit = load_override_tables()
    request_id = _next_id("R", requests["request_id"]) if not requests.empty else "R0001"
    row = {
        "request_id": request_id,
        "store_id": store_id,
        "cluster_id": cluster_id,
        "sku_id": sku_id,
        "field_to_override": field_to_override,
        "old_value": old_value,
        "new_value": new_value,
        "requester": requester,
        "reason_text": reason_text,
        "created_at": _now_str(),
        "status": "submitted",
    }
    requests = pd.concat([requests, pd.DataFrame([row])], ignore_index=True)
    audit = _write_audit(audit, request_id, "submit", requester, row)
    write_table("override_requests", requests)
    write_table("override_audit_log", audit)
    return request_id


def change_request_status(request_id: str, action: str, operator: str) -> None:
    requests, audit = load_override_tables()
    if request_id not in requests["request_id"].values:
        return
    current_status = requests.loc[requests["request_id"] == request_id, "status"].iloc[0]
    status_map = {
        "approve": "approved",
        "reject": "rejected",
        "rollback": "rolled_back",
    }
    new_status = status_map[action]
    requests.loc[requests["request_id"] == request_id, "status"] = new_status
    audit = _write_audit(audit, request_id, action, operator, {"from": current_status, "to": new_status})
    write_table("override_requests", requests)
    write_table("override_audit_log", audit)


def get_active_overrides() -> pd.DataFrame:
    requests, _ = load_override_tables()
    active = requests[requests["status"] == "applied"].copy()
    if active.empty:
        return active
    return active.sort_values("created_at")


def apply_request(
    request_id: str,
    operator: str,
    recommendations: pd.DataFrame,
    products: pd.DataFrame,
    need_states: pd.DataFrame,
    shelf_capacity_cm: float,
    min_facings_core: int,
    max_facings_per_sku: int,
    brand_cap: float,
) -> tuple[bool, str]:
    requests, audit = load_override_tables()
    target = requests[requests["request_id"] == request_id]
    if target.empty:
        return False, "Request not found."
    row = target.iloc[0]
    if row["status"] != "approved":
        return False, "Only approved requests can be applied."

    cluster_id = row["cluster_id"]
    sku_id = row["sku_id"]
    trial = recommendations[recommendations["cluster_id"] == cluster_id][["cluster_id", "sku_id", "facings"]].copy()
    if trial.empty:
        return False, "No recommendation set for selected cluster."
    if sku_id not in trial["sku_id"].values:
        trial = pd.concat([trial, pd.DataFrame([{"cluster_id": cluster_id, "sku_id": sku_id, "facings": 0}])], ignore_index=True)

    field = row["field_to_override"]
    if field == "facings":
        trial.loc[trial["sku_id"] == sku_id, "facings"] = int(float(row["new_value"]))
    elif field == "force_keep":
        trial.loc[trial["sku_id"] == sku_id, "facings"] = max(int(float(row["new_value"])), min_facings_core)
    elif field == "force_delist":
        trial.loc[trial["sku_id"] == sku_id, "facings"] = 0

    ok, errors = validate_cluster_constraints(
        trial,
        products[["sku_id", "shelf_width_cm", "brand", "is_core", "need_state_id"]],
        need_states,
        shelf_capacity_cm,
        min_facings_core,
        max_facings_per_sku,
        brand_cap,
    )
    if not ok:
        audit = _write_audit(
            audit,
            request_id,
            "apply_blocked",
            operator,
            {"errors": errors, "field": field, "new_value": row["new_value"]},
        )
        write_table("override_audit_log", audit)
        return False, "; ".join(errors)

    requests.loc[requests["request_id"] == request_id, "status"] = "applied"
    audit = _write_audit(
        audit,
        request_id,
        "apply",
        operator,
        {"field": field, "new_value": row["new_value"], "cluster_id": cluster_id, "sku_id": sku_id},
    )
    write_table("override_requests", requests)
    write_table("override_audit_log", audit)
    return True, "Override applied."
