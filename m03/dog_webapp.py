"""A small web interface for fetching random dog images."""

from __future__ import annotations

import html
import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


HOST = "localhost"
PORT = 8000
API_URL = "https://api.thedogapi.com/v1/images/search"
API_KEY_VARIABLE = "CS1066_THEDOGAPIKEY"


def fetch_random_dog_url() -> str:
    """Ask The Dog API for one image URL."""
    headers = {"Accept": "application/json"}
    api_key = os.environ.get(API_KEY_VARIABLE)
    if api_key:
        headers["x-api-key"] = api_key

    request = Request(API_URL, headers=headers)
    try:
        with urlopen(request, timeout=20) as response:
            payload = json.load(response)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Could not fetch a dog image: {exc}") from exc

    if not isinstance(payload, list) or not payload:
        raise RuntimeError("The Dog API returned no image data.")

    image_url = payload[0].get("url")
    if not isinstance(image_url, str) or not image_url:
        raise RuntimeError("The Dog API response did not include an image URL.")
    return image_url


def page(image_url: str | None = None, error: str | None = None) -> str:
    """Build the page shown by the local web server."""
    image = (
        f'<img src="{html.escape(image_url, quote=True)}" '
        'alt="A randomly fetched dog" class="dog-photo">'
        if image_url
        else '<div class="placeholder" aria-label="No dog fetched yet">🐾</div>'
    )
    message = (
        f'<p class="error" role="alert">{html.escape(error)}</p>' if error else ""
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Fetch a Dog</title>
  <style>
    :root {{ color-scheme: light; font-family: Georgia, serif; }}
    * {{ box-sizing: border-box; }}
    body {{
      align-items: center; background: #f8f1e8; color: #332b28;
      display: flex; justify-content: center; min-height: 100vh; margin: 0;
      padding: 2rem;
    }}
    main {{
      background: #fffdf9; border: 1px solid #ead9c7; border-radius: 24px;
      box-shadow: 0 18px 50px #8a624329; max-width: 620px; padding: 2rem;
      text-align: center; width: 100%;
    }}
    h1 {{ color: #b85c38; font-size: clamp(2rem, 7vw, 3.5rem); margin: 0; }}
    .subtitle {{ color: #75655d; font-size: 1.1rem; margin: .5rem 0 1.5rem; }}
    .photo-frame {{
      align-items: center; background: #f1e4d5; border-radius: 18px;
      display: flex; justify-content: center; margin: 0 auto 1.5rem;
      min-height: 300px; overflow: hidden;
    }}
    .dog-photo {{ display: block; height: auto; max-height: 500px; max-width: 100%; object-fit: cover; }}
    .placeholder {{ color: #c18b65; font-size: 5rem; padding: 5rem; }}
    button {{
      background: #d96f4c; border: 0; border-radius: 999px; color: white;
      cursor: pointer; font: inherit; font-weight: bold; padding: .85rem 2.4rem;
      transition: background .2s, transform .2s;
    }}
    button:hover {{ background: #b95637; transform: translateY(-2px); }}
    button:focus-visible {{ outline: 3px solid #332b28; outline-offset: 3px; }}
    .error {{ color: #a33d32; margin: 1rem 0 0; }}
  </style>
</head>
<body>
  <main>
    <h1>Fetch a Dog</h1>
    <p class="subtitle">A little joy, one random pup at a time.</p>
    <div class="photo-frame">{image}</div>
    <form method="post" action="/">
      <button type="submit">fetch</button>
    </form>
    {message}
  </main>
</body>
</html>"""


class DogRequestHandler(BaseHTTPRequestHandler):
    """Handle the page and its fetch button."""

    def send_page(self, content: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path != "/":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        self.send_page(page())

    def do_POST(self) -> None:
        if self.path != "/":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        try:
            image_url = fetch_random_dog_url()
        except RuntimeError as exc:
            self.send_page(page(error=str(exc)), HTTPStatus.BAD_GATEWAY)
            return
        self.send_page(page(image_url=image_url))

    def log_message(self, format: str, *args: object) -> None:
        print(f"{self.address_string()} - {format % args}")


def main() -> None:
    """Start the local dog image web app."""
    server = HTTPServer((HOST, PORT), DogRequestHandler)
    print(f"Open http://{HOST}:{PORT} in your browser.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping the dog web app.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
