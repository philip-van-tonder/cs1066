"""Local web dashboard for SEC annual revenue, income, and assets."""

from __future__ import annotations

import base64
import html
import io
import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import data_extraction
import sec_data_fetch


HOST = "127.0.0.1"
PORT = 8000
DEFAULT_CIK = "0000002488"
USER_AGENT = os.environ.get(
    "SEC_USER_AGENT", sec_data_fetch.DEFAULT_USER_AGENT
)


def write_extracted_data(company_data: dict[str, object]) -> list[dict[str, int]]:
    """Extract annual data and persist it using the existing output format."""
    extracted_data = data_extraction.extract_data(company_data)
    data_extraction.OUTPUT_PATH.write_text(
        json.dumps(extracted_data, indent=2) + "\n",
        encoding="utf-8",
    )
    return extracted_data


def chart_data_url(
    years: list[int], values: list[int], title: str, color: str
) -> str:
    """Create a chart and return it as a data URL for embedding in HTML."""
    figure, axis = plt.subplots(figsize=(10, 4.2), dpi=140)
    figure.patch.set_facecolor("#ffffff")
    axis.set_facecolor("#f7f9fc")
    axis.plot(
        years,
        values,
        color=color,
        marker="o",
        linewidth=2.5,
        markersize=6,
    )
    axis.fill_between(years, values, color=color, alpha=0.1)
    axis.set_title(title, loc="left", fontsize=15, fontweight="bold", color="#172b4d")
    axis.set_xlabel("Fiscal year", color="#526173")
    axis.set_ylabel("Value (USD)", color="#526173")
    axis.grid(axis="y", color="#dbe3ee", linewidth=0.8)
    axis.spines[["top", "right"]].set_visible(False)
    axis.spines[["left", "bottom"]].set_color("#b8c4d3")
    axis.tick_params(colors="#526173")
    figure.tight_layout()

    image = io.BytesIO()
    figure.savefig(image, format="png", facecolor=figure.get_facecolor())
    plt.close(figure)
    encoded = base64.b64encode(image.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def render_dashboard(
    company_name: str,
    cik: str,
    annual_data: list[dict[str, int]],
    error: str | None = None,
) -> bytes:
    """Render the dashboard page."""
    safe_company_name = html.escape(company_name)
    safe_cik = html.escape(cik, quote=True)
    message = (
        f'<div class="error">{error}</div>' if error else ""
    )
    if annual_data:
        years = [row["year"] for row in annual_data]
        charts = [
            chart_data_url(
                years,
                [row["revenue"] for row in annual_data],
                "Annual Revenue",
                "#1769aa",
            ),
            chart_data_url(
                years,
                [row["net_income"] for row in annual_data],
                "Net Income",
                "#2e7d9a",
            ),
            chart_data_url(
                years,
                [row["assets"] for row in annual_data],
                "Total Assets",
                "#526d82",
            ),
        ]
        chart_html = "".join(
            f'<img class="chart" src="{chart}" alt="{title} chart">'
            for chart, title in zip(
                charts, ("Annual revenue", "Net income", "Total assets")
            )
        )
        summary = (
            f'<p class="summary">Showing {len(annual_data)} annual 10-K periods '
            f'from {years[0]} through {years[-1]}.</p>'
        )
    else:
        chart_html = ""
        summary = (
            '<p class="summary">No complete annual 10-K data was found for '
            "this company.</p>"
        )

    page_html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Financial Dashboard</title>
  <style>
    :root {{ font-family: "Segoe UI", Arial, sans-serif; color: #172b4d; }}
    body {{ margin: 0; background: #eef2f7; }}
    header {{ background: #123b63; color: white; padding: 28px max(24px, calc((100% - 1040px) / 2)); }}
    header h1 {{ margin: 0 0 5px; font-size: 30px; }}
    header p {{ margin: 0; color: #cbd9e8; }}
    main {{ max-width: 1040px; margin: 26px auto 50px; padding: 0 24px; }}
    .panel {{ background: white; border: 1px solid #d7e0eb; border-radius: 8px; padding: 22px; box-shadow: 0 3px 12px #1c35570d; }}
    form {{ display: flex; gap: 12px; align-items: end; flex-wrap: wrap; }}
    label {{ display: flex; flex-direction: column; gap: 7px; font-weight: 600; color: #526173; }}
    input {{ width: 220px; padding: 11px 12px; border: 1px solid #b8c4d3; border-radius: 5px; font: inherit; color: #172b4d; }}
    button {{ padding: 12px 20px; border: 0; border-radius: 5px; background: #1769aa; color: white; font: inherit; font-weight: 600; cursor: pointer; }}
    button:hover {{ background: #0f568d; }}
    .summary {{ color: #526173; margin: 20px 0 12px; }}
    .error {{ margin-top: 16px; padding: 12px; border-radius: 5px; color: #8a1c1c; background: #fff0f0; border: 1px solid #efb5b5; }}
    .chart {{ display: block; width: 100%; margin: 18px 0; border: 1px solid #d7e0eb; border-radius: 5px; }}
    .company {{ margin-top: 24px; font-size: 20px; font-weight: 600; }}
    @media (max-width: 600px) {{ input {{ width: 100%; }} button {{ width: 100%; }} }}
  </style>
</head>
<body>
  <header>
    <h1>Financial Dashboard</h1>
    <p>Annual SEC filing trends for revenue, net income, and total assets</p>
  </header>
  <main>
    <section class="panel">
      <form method="post">
        <label>Company CIK
          <input name="cik" value="{safe_cik}" required inputmode="numeric"
                 pattern="[0-9]{{10}}" maxlength="10"
                 placeholder="e.g. 0000002488">
        </label>
        <button type="submit">Load financials</button>
      </form>
      {message}
      <div class="company">{safe_company_name}</div>
      {summary}
      {chart_html}
    </section>
  </main>
</body>
</html>"""
    return page_html.encode("utf-8")


class DashboardHandler(BaseHTTPRequestHandler):
    """Handle dashboard requests."""

    def do_GET(self) -> None:
        """Display the initial dashboard page."""
        query = parse_qs(urlparse(self.path).query)
        cik = query.get("cik", [DEFAULT_CIK])[0]
        self.send_page("Enter a CIK to load company data.", cik)

    def do_POST(self) -> None:
        """Fetch and display data for the submitted CIK."""
        length = int(self.headers.get("Content-Length", "0"))
        form_data = parse_qs(self.rfile.read(length).decode("utf-8"))
        raw_cik = form_data.get("cik", [""])[0]
        try:
            cik = sec_data_fetch.validate_cik(raw_cik)
            company_data = sec_data_fetch.fetch_company_facts(cik, USER_AGENT)
            annual_data = write_extracted_data(company_data)
            company_name = str(company_data.get("entityName", "Company"))
            self.send_page(None, cik, company_name, annual_data)
        except (ValueError, RuntimeError, OSError, TypeError, json.JSONDecodeError) as error:
            self.send_page(str(error), raw_cik)

    def send_page(
        self,
        error: str | None,
        cik: str,
        company_name: str = "Financial Dashboard",
        annual_data: list[dict[str, int]] | None = None,
    ) -> None:
        """Send a rendered HTML page."""
        page = render_dashboard(company_name, cik, annual_data or [], error)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(page)

    def log_message(self, format: str, *args: object) -> None:
        """Keep the server log concise."""
        print(f"[dashboard] {format % args}")


def main() -> None:
    """Start the local dashboard server."""
    server = ThreadingHTTPServer((HOST, PORT), DashboardHandler)
    print(f"Financial dashboard running at http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping dashboard.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
