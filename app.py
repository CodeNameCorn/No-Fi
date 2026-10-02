import os
from flask import Flask, request, render_template
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    images = []
    error = ""
    url = ""

    if request.method == "POST":
        url = request.form.get("url", "").strip()
        parsed = urlparse(url)

        if parsed.scheme != "https" or parsed.hostname not in (
            "ko-fi.com",
            "www.ko-fi.com"
        ):
            error = "Enter a valid HTTPS Ko-fi URL."

        else:
            try:
                response = requests.get(
                    url,
                    headers={"User-Agent": "Mozilla/5.0"},
                    timeout=15
                )

                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")

                for tag in soup.find_all("meta"):
                    if (
                        tag.get("property") in ("og:image", "og:image:url")
                        or tag.get("name") == "twitter:image"
                    ):
                        src = tag.get("content")
                        if src:
                            images.append(urljoin(url, src))

                for tag in soup.find_all("img"):
                    src = (
                        tag.get("src")
                        or tag.get("data-src")
                        or tag.get("data-lazy-src")
                    )

                    if src:
                        images.append(urljoin(url, src))

                images = list(dict.fromkeys(images))[:60]

                if not images:
                    error = (
                        "No public images found. "
                        "Some pages load content dynamically."
                    )

            except requests.RequestException:
                error = "Could not load the page. Check the URL."

    return render_template(
        "index.html",
        images=images,
        error=error,
        url=url
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
