"""Fetch SEC EDGAR company facts for a CIK and save them as JSON."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


SEC_COMPANY_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
OUTPUT_PATH = Path(__file__).with_name("company_data.json")
DEFAULT_USER_AGENT = (
    "CS1066 financial analysis tool (contact: student@example.com)"
)


def validate_cik(value: str) -> str:
    """Return a validated ten-digit CIK."""
    cik = value.strip()
    if len(cik) != 10 or not cik.isdigit():
        raise ValueError("CIK must contain exactly 10 digits.")
    return cik


def fetch_company_facts(cik: str, user_agent: str) -> dict[str, Any]:
    """Fetch the raw company facts JSON document from the SEC."""
    request = Request(
        SEC_COMPANY_FACTS_URL.format(cik=cik),
        headers={
            "Accept": "application/json",
            "User-Agent": user_agent,
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            facts = json.load(response)
    except HTTPError as error:
        if error.code == 404:
            raise RuntimeError("The SEC could not find that CIK.") from error
        raise RuntimeError(f"The SEC returned HTTP {error.code}.") from error
    except URLError as error:
        raise RuntimeError(f"Could not reach the SEC: {error.reason}") from error
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RuntimeError("The SEC returned invalid JSON.") from error

    if not isinstance(facts, dict):
        raise RuntimeError("The SEC returned an unexpected JSON document.")
    return facts


def write_company_data(company_data: dict[str, Any]) -> None:
    """Write the company facts document to the required output file."""
    OUTPUT_PATH.write_text(
        json.dumps(company_data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    """Read a CIK, fetch company facts, and save the response."""
    raw_cik = sys.argv[1] if len(sys.argv) > 1 else input("Enter a 10-digit CIK: ")
    try:
        cik = validate_cik(raw_cik)
        user_agent = os.environ.get("SEC_USER_AGENT", DEFAULT_USER_AGENT)
        company_data = fetch_company_facts(cik, user_agent)
        write_company_data(company_data)
    except (ValueError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    company_name = company_data.get("entityName", "company")
    print(f"Saved company facts for {company_name} to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
