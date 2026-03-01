from __future__ import annotations

import pandas as pd

CORE_SIZES = ("NB", "S", "M", "L")
CORE_FORMATS = ("腰贴", "拉拉裤")


def pack_tier(pack_count: int) -> str:
    if pack_count <= 32:
        return "small_pack"
    if pack_count <= 60:
        return "mid_pack"
    return "bulk_pack"


def attach_need_states(products: pd.DataFrame) -> pd.DataFrame:
    enriched = products.copy()
    diapers = enriched["category"] == "diaper"
    enriched.loc[diapers, "pack_tier"] = enriched.loc[diapers, "pack_count"].astype(int).map(pack_tier)
    enriched.loc[~diapers, "pack_tier"] = "na"
    enriched.loc[diapers, "need_state_id"] = (
        enriched.loc[diapers, "size"]
        + "|"
        + enriched.loc[diapers, "format"]
        + "|"
        + enriched.loc[diapers, "price_tier"]
        + "|"
        + enriched.loc[diapers, "pack_tier"]
    )
    enriched.loc[~diapers, "need_state_id"] = "na"
    enriched.loc[diapers, "coverage_group_id"] = enriched.loc[diapers, "size"] + "|" + enriched.loc[diapers, "format"]
    enriched.loc[~diapers, "coverage_group_id"] = "na"
    enriched.loc[diapers, "is_core"] = (
        enriched.loc[diapers, "size"].isin(CORE_SIZES) & enriched.loc[diapers, "format"].isin(CORE_FORMATS)
    ).astype(int)
    return enriched


def build_need_state_dict(products: pd.DataFrame) -> pd.DataFrame:
    diapers = products[products["category"] == "diaper"].copy()
    need_state_dict = (
        diapers[
            [
                "need_state_id",
                "size",
                "format",
                "price_tier",
                "pack_tier",
                "coverage_group_id",
                "is_core",
            ]
        ]
        .drop_duplicates()
        .sort_values(["size", "format", "price_tier", "pack_tier"])
        .reset_index(drop=True)
    )
    return need_state_dict


def required_core_coverage_groups() -> list[str]:
    return [f"{size}|{diaper_format}" for size in CORE_SIZES for diaper_format in CORE_FORMATS]
