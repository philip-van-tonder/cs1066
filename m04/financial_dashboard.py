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
PLOT_TYPES = ("line", "bar", "area")
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


def plot_buttons(
    metric: str, selected: str, plot_types: dict[str, str], cik: str
) -> str:
    """Render compact graphic controls for one metric."""
    hidden_fields = "".join(
        f'<input type="hidden" name="{name}_plot" value="{plot_types[name]}">'
        for name in ("revenue", "net_income", "assets")
        if name != metric
    )
    buttons = "".join(
        f'<button class="plot-button{" active" if plot_type == selected else ""}" '
        f'name="{metric}_plot" value="{plot_type}" type="submit" '
        f'aria-label="Show {plot_type} plot">{plot_type[0].upper()}</button>'
        for plot_type in PLOT_TYPES
    )
    return (
        f'<form class="chart-controls" method="post">'
        f'<input type="hidden" name="cik" value="{html.escape(cik, quote=True)}">'
        f"{hidden_fields}{buttons}</form>"
    )


def get_plot_types(form_data: dict[str, list[str]]) -> dict[str, str]:
    """Return validated plot types submitted for each metric."""
    return {
        metric: (
            form_data.get(f"{metric}_plot", ["line"])[0]
            if form_data.get(f"{metric}_plot", ["line"])[0] in PLOT_TYPES
            else "line"
        )
        for metric in ("revenue", "net_income", "assets")
    }


def chart_data_url(
    years: list[int],
    values: list[int],
    title: str,
    color: str,
    plot_type: str,
) -> str:
    """Create a chart and return it as a data URL for embedding in HTML."""
    figure, axis = plt.subplots(figsize=(4.5, 2.7), dpi=140)
    scaled_values = [value / 1_000_000_000 for value in values]
    figure.patch.set_facecolor("#ffffff")
    axis.set_facecolor("#f4f7fb")
    if plot_type == "bar":
        axis.bar(years, scaled_values, color=color, width=0.7)
    else:
        axis.plot(
            years,
            scaled_values,
            color=color,
            marker="o",
            linewidth=2.2,
            markersize=4,
        )
        if plot_type == "area":
            axis.fill_between(years, scaled_values, color=color, alpha=0.16)
    axis.set_title(
        title,
        loc="left",
        fontsize=13,
        fontweight="bold",
        fontfamily="DejaVu Serif",
        color="#082c54",
    )
    axis.set_xlabel("Fiscal year", color="#24496f", fontsize=8)
    axis.set_ylabel("Value (USD, billions)", color="#24496f", fontsize=8)
    axis.set_xticks(years)
    axis.set_xticklabels([str(year) for year in years], rotation=45, ha="right")
    axis.grid(axis="y", color="#c8d5e5", linewidth=0.7)
    axis.spines[["top", "right"]].set_visible(False)
    axis.spines[["left", "bottom"]].set_color("#7893b0")
    axis.tick_params(colors="#24496f", labelsize=7)
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
    plot_types: dict[str, str] | None = None,
) -> bytes:
    """Render the dashboard page."""
    safe_company_name = html.escape(company_name)
    safe_cik = html.escape(cik, quote=True)
    selected_plot_types = {
        metric: plot_types.get(metric, "line") if plot_types else "line"
        for metric in ("revenue", "net_income", "assets")
    }
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
                "#0b4f8a",
                selected_plot_types["revenue"],
            ),
            chart_data_url(
                years,
                [row["net_income"] for row in annual_data],
                "Net Income",
                "#0b4f8a",
                selected_plot_types["net_income"],
            ),
            chart_data_url(
                years,
                [row["assets"] for row in annual_data],
                "Total Assets",
                "#0b4f8a",
                selected_plot_types["assets"],
            ),
        ]
        metrics = (
            ("revenue", "Revenue"),
            ("net_income", "Net income"),
            ("assets", "Assets"),
        )
        chart_html = "".join(
            f'<figure><div class="chart-heading"><figcaption>{title}</figcaption>'
            f"{plot_buttons(metric, selected_plot_types[metric], selected_plot_types, cik)}"
            f'</div><img class="chart" src="{chart}" alt="{title} chart"></figure>'
            for chart, (metric, title) in zip(charts, metrics)
        )
        summary = (
            f'<p class="summary">Showing {len(annual_data)} annual 10-K periods '
            f'from {years[0]} through {years[-1]}.</p>'
        )
    else:
        chart_html = ""
        summary = (
            '<p class="summary warning">No complete annual 10-K data was found for '
            "this company.</p>"
        )

    page_html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Financial Dashboard</title>
  <style>
    :root {{ font-family: "Segoe UI", Arial, sans-serif; color: #102f50; }}
    html, body {{ min-height: 100%; }}
    body {{ margin: 0; background: #e8eef5; }}
    header {{ background: #061f3d; color: white; padding: 18px 28px; }}
    header h1 {{ margin: 0 0 3px; font-family: "Aptos Display", "Helvetica Neue", Arial, sans-serif; font-size: 29px; font-weight: 800; letter-spacing: .015em; }}
    header p {{ margin: 0; color: #cbd9e8; }}
    main {{ width: 100%; min-height: calc(100vh - 77px); box-sizing: border-box; padding: 14px; }}
    .panel {{ min-height: calc(100vh - 105px); box-sizing: border-box; background: white; border: 1px solid #c5d3e2; padding: 14px; box-shadow: 0 2px 8px #102f5014; }}
    form {{ display: flex; gap: 10px; align-items: end; flex-wrap: wrap; }}
    label {{ display: flex; flex-direction: column; gap: 4px; font-weight: 600; color: #24496f; font-size: 13px; }}
    input, select {{ padding: 8px 9px; border: 1px solid #9eb2c9; font: inherit; color: #102f50; background: white; }}
    .dashboard-form input, .dashboard-form button {{ height: 38px; box-sizing: border-box; }}
    .dashboard-form input {{ width: 190px; }}
    button {{ padding: 9px 16px; border: 0; background: #0b4f8a; color: white; font: inherit; font-weight: 600; cursor: pointer; }}
    button:hover {{ background: #07365f; }}
    .summary {{ color: #385878; margin: 10px 0 7px; font-size: 13px; }}
    .error, .warning {{ margin-top: 10px; padding: 9px; color: #075985; background: #dff2ff; border: 1px solid #9bd3f5; }}
    .charts {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; }}
    figure {{ margin: 0; min-width: 0; }}
    .chart-heading {{ display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 4px; }}
    .chart {{ display: block; width: 100%; border: 1px solid #c5d3e2; }}
    figcaption {{ color: #24496f; font-size: 12px; font-weight: 700; }}
    .chart-controls {{ display: flex; gap: 2px; margin: 0; }}
    .plot-button {{ padding: 3px 7px; background: #d7e8f7; color: #16466d; font-size: 10px; font-weight: 700; }}
    .plot-button:hover, .plot-button.active {{ background: #0b4f8a; color: white; }}
    .company {{ margin-top: 10px; font-family: Georgia, serif; font-size: 19px; font-weight: 700; color: #082c54; }}
    @media (max-width: 800px) {{ .charts {{ grid-template-columns: 1fr; }} }}
    @media (max-width: 600px) {{ .dashboard-form input {{ width: 100%; }} .dashboard-form button {{ width: 100%; }} }}
  </style>
</head>
<body>
  <header>
    <h1>Financial Dashboard</h1>
    <p>Annual SEC filing trends for revenue, net income, and total assets</p>
  </header>
  <main>
    <section class="panel">
      <form class="dashboard-form" method="post">
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
      <div class="charts">{chart_html}</div>
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
        raw_cik = query.get("cik", [DEFAULT_CIK])[0]
        try:
            cik = sec_data_fetch.validate_cik(raw_cik)
        except ValueError as error:
            self.send_page(str(error), raw_cik)
            return
        self.send_page("Enter a CIK to load company data.", cik)

    def do_POST(self) -> None:
        """Fetch and display data for the submitted CIK."""
        length = int(self.headers.get("Content-Length", "0"))
        form_data = parse_qs(self.rfile.read(length).decode("utf-8"))
        raw_cik = form_data.get("cik", [""])[0]
        plot_types = get_plot_types(form_data)
        try:
            cik = sec_data_fetch.validate_cik(raw_cik)
            company_data = sec_data_fetch.fetch_company_facts(cik, USER_AGENT)
            annual_data = write_extracted_data(company_data)
            company_name = str(company_data.get("entityName", "Company"))
            self.send_page(None, cik, company_name, annual_data, plot_types)
        except (ValueError, RuntimeError, OSError, TypeError, json.JSONDecodeError) as error:
            self.send_page(str(error), raw_cik, plot_types=plot_types)

    def send_page(
        self,
        error: str | None,
        cik: str,
        company_name: str = "Financial Dashboard",
        annual_data: list[dict[str, int]] | None = None,
        plot_types: dict[str, str] | None = None,
    ) -> None:
        """Send a rendered HTML page."""
        page = render_dashboard(
            company_name, cik, annual_data or [], error, plot_types
        )
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
