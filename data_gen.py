from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd


def _sku_price(size: str, diaper_format: str, price_tier: str, variant: int) -> float:
    tier_base = {"good": 72.0, "better": 92.0, "best": 118.0}[price_tier]
    size_lift = {"NB": -6.0, "S": 0.0, "M": 6.0, "L": 12.0, "XL": 18.0}[size]
    format_lift = 10.0 if diaper_format == "拉拉裤" else 0.0
    return tier_base + size_lift + format_lift + variant * 2.5


def _pack_count(price_tier: str, variant: int) -> int:
    base = {"good": 28, "better": 48, "best": 72}[price_tier]
    return base + variant * 4


def _build_products() -> pd.DataFrame:
    sizes = ["NB", "S", "M", "L", "XL"]
    formats = ["腰贴", "拉拉裤"]
    price_tiers = ["good", "better", "best"]
    brands = ["Pampers", "Huggies", "MamyPoko", "BabySoft"]
    rows: list[dict[str, object]] = []
    sku_index = 1
    for size_idx, size in enumerate(sizes):
        for format_idx, diaper_format in enumerate(formats):
            for tier_idx, price_tier in enumerate(price_tiers):
                for variant in range(2):
                    brand = brands[(size_idx + format_idx + tier_idx + variant) % len(brands)]
                    retail = _sku_price(size, diaper_format, price_tier, variant)
                    width = {"good": 7.0, "better": 8.0, "best": 9.0}[price_tier] + variant * 0.5
                    rows.append(
                        {
                            "sku_id": f"D{sku_index:03d}",
                            "category": "diaper",
                            "brand": brand,
                            "size": size,
                            "format": diaper_format,
                            "pack_count": _pack_count(price_tier, variant),
                            "price_tier": price_tier,
                            "unit_cost": round(retail * (0.60 + 0.03 * tier_idx), 2),
                            "shelf_width_cm": width,
                            "is_kvi": int(price_tier == "good" and size in {"NB", "S", "M", "L"}),
                            "is_core": int(size in {"NB", "S", "M", "L"}),
                            "is_private_label": int(brand == "BabySoft"),
                        }
                    )
                    sku_index += 1

    for idx in range(1, 7):
        retail = 9.9 + (idx % 3) * 3.0
        rows.append(
            {
                "sku_id": f"W{idx:03d}",
                "category": "wipes",
                "brand": brands[idx % len(brands)],
                "size": "NA",
                "format": "湿巾",
                "pack_count": 80 if idx % 2 == 0 else 40,
                "price_tier": ["good", "better", "best"][idx % 3],
                "unit_cost": round(retail * 0.52, 2),
                "shelf_width_cm": 4.0,
                "is_kvi": 0,
                "is_core": 0,
                "is_private_label": int(brands[idx % len(brands)] == "BabySoft"),
            }
        )

    for idx in range(1, 5):
        retail = 24.0 + idx * 4.0
        rows.append(
            {
                "sku_id": f"C{idx:03d}",
                "category": "cream",
                "brand": brands[(idx + 1) % len(brands)],
                "size": "NA",
                "format": "护臀霜",
                "pack_count": 1,
                "price_tier": ["good", "better", "best"][idx % 3],
                "unit_cost": round(retail * 0.48, 2),
                "shelf_width_cm": 3.0,
                "is_kvi": 0,
                "is_core": 0,
                "is_private_label": int(brands[(idx + 1) % len(brands)] == "BabySoft"),
            }
        )

    return pd.DataFrame(rows)


def _build_stores() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    formats = ["Hyper", "Hyper", "Hyper", "Super", "Super", "Super", "Super", "Super", "CVS", "CVS", "CVS", "CVS"]
    incomes = [5, 4, 3, 4, 3, 2, 5, 3, 2, 1, 4, 2]
    regions = ["East", "South", "North", "West"]
    for idx, store_format in enumerate(formats, start=1):
        rows.append(
            {
                "store_id": f"S{idx:03d}",
                "store_format": store_format,
                "income_proxy": incomes[idx - 1],
                "region": regions[(idx - 1) % len(regions)],
                "baseline_gp": float({"Hyper": 14000, "Super": 9000, "CVS": 5200}[store_format] + idx * 180),
                "trade_area_id": f"TA{((idx - 1) // 3) + 1:02d}",
            }
        )
    return pd.DataFrame(rows)


def _build_baseline_assortment(
    rng: np.random.Generator, stores: pd.DataFrame, products: pd.DataFrame
) -> pd.DataFrame:
    diapers = products[products["category"] == "diaper"].copy()
    core_groups = [(size, diaper_format) for size in ["NB", "S", "M", "L"] for diaper_format in ["腰贴", "拉拉裤"]]
    rows: list[dict[str, object]] = []

    for store in stores.itertuples():
        target_count = {"Hyper": 24, "Super": 18, "CVS": 14}[store.store_format]
        chosen: set[str] = set()
        for size, diaper_format in core_groups:
            candidates = diapers[(diapers["size"] == size) & (diapers["format"] == diaper_format)]
            preferred = candidates.sort_values(["is_kvi", "price_tier"], ascending=[False, True]).iloc[
                (store.income_proxy + len(chosen)) % len(candidates)
            ]
            chosen.add(str(preferred["sku_id"]))

        remaining = diapers[~diapers["sku_id"].isin(chosen)]
        extra = remaining.sample(target_count - len(chosen), random_state=int(rng.integers(1, 100_000)))
        chosen.update(extra["sku_id"].tolist())

        for sku in diapers.itertuples():
            listed = int(sku.sku_id in chosen)
            facings = 0
            if listed:
                facings = 2 if sku.is_core else 1
                if sku.is_kvi:
                    facings += 1
                if store.store_format == "Hyper" and sku.price_tier == "better":
                    facings += 1
                facings = int(min(facings, 4))
            rows.append(
                {
                    "store_id": store.store_id,
                    "sku_id": sku.sku_id,
                    "is_listed": listed,
                    "facings": facings,
                }
            )
    return pd.DataFrame(rows)


def _build_inventory_daily(
    rng: np.random.Generator, stores: pd.DataFrame, products: pd.DataFrame, baseline_assortment: pd.DataFrame
) -> pd.DataFrame:
    diapers = products[products["category"] == "diaper"].copy()
    listed = baseline_assortment[baseline_assortment["is_listed"] == 1].merge(
        diapers[["sku_id", "price_tier", "format", "is_core"]],
        on="sku_id",
        how="left",
    )
    dates = pd.date_range("2026-01-01", periods=56, freq="D")
    rows: list[dict[str, object]] = []
    for row in listed.itertuples():
        for date in dates:
            base_cover = 12 + row.facings * 5 + (2 if row.is_core else 0)
            oos_prob = 0.04 + (0.02 if row.price_tier == "good" else 0.0) + (0.02 if row.format == "拉拉裤" else 0.0)
            oos_prob -= 0.01 * row.facings
            oos_prob = float(np.clip(oos_prob, 0.01, 0.18))
            oos_flag = int(rng.random() < oos_prob)
            on_hand = max(0, int(base_cover + rng.normal(0, 3) - 6 * oos_flag))
            rows.append(
                {
                    "store_id": row.store_id,
                    "sku_id": row.sku_id,
                    "date": date.strftime("%Y-%m-%d"),
                    "on_hand": on_hand,
                    "oos_flag": oos_flag,
                }
            )
    return pd.DataFrame(rows)


def _weighted_choice(rng: np.random.Generator, values: list[str], weights: list[float]) -> str:
    probs = np.array(weights, dtype=float)
    probs = probs / probs.sum()
    return str(rng.choice(values, p=probs))


def _build_transactions(
    rng: np.random.Generator,
    stores: pd.DataFrame,
    products: pd.DataFrame,
    baseline_assortment: pd.DataFrame,
) -> pd.DataFrame:
    diapers = products[products["category"] == "diaper"].copy()
    accessories = products[products["category"] != "diaper"].copy()
    diaper_lookup = diapers.set_index("sku_id")
    accessory_lookup = accessories.set_index("sku_id")
    listed_lookup = (
        baseline_assortment[baseline_assortment["is_listed"] == 1]
        .groupby("store_id")["sku_id"]
        .apply(list)
        .to_dict()
    )
    dates = pd.date_range("2026-01-01", periods=56, freq="D")
    basket_counter = 1
    rows: list[dict[str, object]] = []

    for store in stores.itertuples():
        store_skus = listed_lookup[store.store_id]
        daily_baskets = {"Hyper": 26, "Super": 18, "CVS": 12}[store.store_format]
        for day_idx, date in enumerate(dates):
            for _ in range(daily_baskets):
                basket_id = f"B{basket_counter:07d}"
                basket_counter += 1
                customer_id = f"CUST{int(rng.integers(10_000, 99_999))}"
                weights: list[float] = []
                for sku_id in store_skus:
                    sku = diaper_lookup.loc[sku_id]
                    score = 1.0
                    if store.income_proxy >= 4 and sku["price_tier"] in {"better", "best"}:
                        score += 0.45
                    if store.income_proxy <= 2 and sku["price_tier"] == "good":
                        score += 0.40
                    if store.store_format == "CVS" and sku["pack_count"] > 60:
                        score -= 0.20
                    if sku["format"] == "拉拉裤":
                        score += 0.15 + day_idx / 400.0
                    if sku["format"] == "腰贴":
                        score += 0.12 - day_idx / 450.0
                    if sku["size"] in {"M", "L"}:
                        score += 0.20
                    if sku["is_kvi"] == 1:
                        score += 0.10
                    weights.append(max(score, 0.05))

                diaper_sku = _weighted_choice(rng, store_skus, weights)
                diaper = diaper_lookup.loc[diaper_sku]
                list_price = _sku_price(str(diaper["size"]), str(diaper["format"]), str(diaper["price_tier"]), int((diaper["pack_count"] - _pack_count(str(diaper["price_tier"]), 0)) / 4))
                promo_prob = 0.26 if diaper["price_tier"] == "good" else 0.14
                promo_flag = int(rng.random() < promo_prob)
                sell_price = list_price * (rng.uniform(0.86, 0.94) if promo_flag else rng.uniform(0.98, 1.03))
                qty = int(1 if rng.random() < 0.86 else 2)
                rows.append(
                    {
                        "basket_id": basket_id,
                        "customer_id": customer_id,
                        "store_id": store.store_id,
                        "date": date.strftime("%Y-%m-%d"),
                        "sku_id": diaper_sku,
                        "qty": qty,
                        "price": round(float(sell_price), 2),
                        "promo_flag": promo_flag,
                    }
                )

                wipes_prob = 0.22 + (0.08 if diaper["price_tier"] == "best" else 0.0) + (0.06 if diaper["format"] == "拉拉裤" else 0.0)
                if rng.random() < min(wipes_prob, 0.48):
                    wipes_ids = accessories[accessories["category"] == "wipes"]["sku_id"].tolist()
                    wipes_sku = _weighted_choice(rng, wipes_ids, [1.2 if accessory_lookup.loc[i, "brand"] == diaper["brand"] else 1.0 for i in wipes_ids])
                    rows.append(
                        {
                            "basket_id": basket_id,
                            "customer_id": customer_id,
                            "store_id": store.store_id,
                            "date": date.strftime("%Y-%m-%d"),
                            "sku_id": wipes_sku,
                            "qty": 1,
                            "price": round(float(10.5 + rng.uniform(-1.2, 4.0)), 2),
                            "promo_flag": 0,
                        }
                    )

                cream_prob = 0.08 + (0.04 if diaper["price_tier"] == "best" else 0.0)
                if rng.random() < min(cream_prob, 0.22):
                    cream_ids = accessories[accessories["category"] == "cream"]["sku_id"].tolist()
                    cream_sku = _weighted_choice(rng, cream_ids, [1.1 if accessory_lookup.loc[i, "brand"] == diaper["brand"] else 1.0 for i in cream_ids])
                    rows.append(
                        {
                            "basket_id": basket_id,
                            "customer_id": customer_id,
                            "store_id": store.store_id,
                            "date": date.strftime("%Y-%m-%d"),
                            "sku_id": cream_sku,
                            "qty": 1,
                            "price": round(float(28.0 + rng.uniform(-3.5, 8.0)), 2),
                            "promo_flag": 0,
                        }
                    )
    return pd.DataFrame(rows)


def generate_demo_data(seed: int = 7) -> Dict[str, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    products = _build_products()
    stores = _build_stores()
    baseline_assortment = _build_baseline_assortment(rng, stores, products)
    inventory_daily = _build_inventory_daily(rng, stores, products, baseline_assortment)
    transactions = _build_transactions(rng, stores, products, baseline_assortment)
    return {
        "transactions": transactions,
        "products": products,
        "stores": stores,
        "inventory_daily": inventory_daily,
        "baseline_assortment": baseline_assortment,
    }
