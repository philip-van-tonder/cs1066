"""Extract annual revenue, net income, and assets from SEC company facts."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any


INPUT_PATH = Path(__file__).with_name("company_data.json")
OUTPUT_PATH = Path(__file__).with_name("revenue_income_asset_data.json")

ASSETS_KEY = "Assets"
NET_INCOME_KEY = "NetIncomeLoss"
CURRENT_REVENUE_KEY = "RevenueFromContractWithCustomerExcludingAssessedTax"
LEGACY_REVENUE_KEY = "SalesRevenueNet"
REVENUE_SWITCH_YEAR = 2018


def parse_date(value: Any) -> date | None:
    """Return an ISO date, or None when the value is not a valid date."""
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def annual_rows(fact: dict[str, Any]) -> list[dict[str, Any]]:
    """Return fact rows that come from complete fiscal-year 10-K filings."""
    units = fact.get("units", {})
    if not isinstance(units, dict):
        return []

    rows: list[dict[str, Any]] = []
    for unit_rows in units.values():
        if not isinstance(unit_rows, list):
            continue
        for row in unit_rows:
            if (
                isinstance(row, dict)
                and row.get("form") == "10-K"
                and row.get("fp") == "FY"
                and isinstance(row.get("fy"), int)
                and isinstance(row.get("val"), (int, float))
            ):
                rows.append(row)
    return rows


def select_assets(rows: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    """Select the latest balance-sheet value reported for each fiscal year."""
    selected: dict[int, dict[str, Any]] = {}
    for row in rows:
        end = parse_date(row.get("end"))
        if end is None:
            continue
        year = row["fy"]
        current = selected.get(year)
        current_end = parse_date(current.get("end")) if current else None
        if current_end is None or end > current_end or (
            end == current_end
            and str(row.get("filed", "")) > str(current.get("filed", ""))
        ):
            selected[year] = row
    return selected


def select_annual_duration(rows: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    """Select the longest duration value reported for each fiscal year."""
    selected: dict[int, dict[str, Any]] = {}
    for row in rows:
        start = parse_date(row.get("start"))
        end = parse_date(row.get("end"))
        if start is None or end is None or end <= start:
            continue
        duration = (end - start).days
        if duration < 300:
            continue

        year = row["fy"]
        current = selected.get(year)
        current_start = parse_date(current.get("start")) if current else None
        current_end = parse_date(current.get("end")) if current else None
        current_duration = (
            (current_end - current_start).days
            if current_start is not None and current_end is not None
            else -1
        )
        exact_year = end.year == year
        current_exact_year = current_end is not None and current_end.year == year
        if (exact_year and not current_exact_year) or (
            exact_year == current_exact_year
            and duration > current_duration
        ) or (
            exact_year == current_exact_year
            and duration == current_duration
            and str(row.get("filed", "")) > str(current.get("filed", ""))
        ):
            selected[year] = row
    return selected


def select_revenue(
    current_rows: list[dict[str, Any]], legacy_rows: list[dict[str, Any]]
) -> dict[int, dict[str, Any]]:
    """Use the current revenue tag from 2018 and the legacy tag before 2018."""
    current_revenue = select_annual_duration(current_rows)
    legacy_revenue = select_annual_duration(legacy_rows)
    return {
        **{
            year: row
            for year, row in legacy_revenue.items()
            if year < REVENUE_SWITCH_YEAR
        },
        **{
            year: row
            for year, row in current_revenue.items()
            if year >= REVENUE_SWITCH_YEAR
        },
    }


def extract_data(company_data: dict[str, Any]) -> list[dict[str, int]]:
    """Extract up to the ten most recent complete financial years."""
    facts = company_data.get("facts", {})
    us_gaap = facts.get("us-gaap", {}) if isinstance(facts, dict) else {}
    if not isinstance(us_gaap, dict):
        return []

    fact_rows: dict[str, list[dict[str, Any]]] = {}
    for key in (
        ASSETS_KEY,
        NET_INCOME_KEY,
        CURRENT_REVENUE_KEY,
        LEGACY_REVENUE_KEY,
    ):
        fact = us_gaap.get(key)
        if isinstance(fact, dict):
            fact_rows[key] = annual_rows(fact)
        else:
            fact_rows[key] = []

    assets = select_assets(fact_rows[ASSETS_KEY])
    net_income = select_annual_duration(fact_rows[NET_INCOME_KEY])
    revenue = select_revenue(
        fact_rows[CURRENT_REVENUE_KEY], fact_rows[LEGACY_REVENUE_KEY]
    )
    years = sorted(set(assets) & set(net_income) & set(revenue), reverse=True)[:10]

    return [
        {
            "year": year,
            "revenue": revenue[year]["val"],
            "net_income": net_income[year]["val"],
            "assets": assets[year]["val"],
        }
        for year in sorted(years)
    ]


def main() -> int:
    """Read company facts and write the extracted annual data."""
    with INPUT_PATH.open(encoding="utf-8") as input_file:
        company_data = json.load(input_file)
    extracted_data = extract_data(company_data)
    with OUTPUT_PATH.open("w", encoding="utf-8") as output_file:
        json.dump(extracted_data, output_file, indent=2)
        output_file.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
