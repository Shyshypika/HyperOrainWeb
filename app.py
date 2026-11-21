from flask import Flask, request, render_template_string
from duckduckgo_search import DDGS
from readability import Document
import requests

app = Flask(__name__)

WORKER_URL = "https://hyperorianvpn1.yangdaniel64.workers.dev/"

HOME_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>HyperOrainWeb</title>
    <style>
        body { font-family: system-ui, sans-serif; background: #121218; color: #fff; margin: 0; padding: 40px 20px; text-align: center; }
        h1 { color: #a29bfe; margin-bottom: 20px; }
        form { display: flex; justify-content: center; gap: 8px; max-width: 560px; margin: 0 auto; }
        input[type="text"] { flex: 1; padding: 10px 14px; border-radius: 6px; border: 1px solid #444; background: #2a2a36; color: #fff; font-size: 16px; }
        input[type="submit"] { padding: 10px 18px; border: none; border-radius: 6px; background: #6c5ce7; color: #fff; font-weight: 600; cursor: pointer; font-size: 16px; }
    </style>
</head>
<body>
    <h1>HyperOrain</h1>
    <form action="/search" method="get">
        <input type="text" name="q" placeholder="Search Retro Search with proxy." required>
        <input type="submit" value="Search">
    </form>
    <h2>DuckDuckGo engine 2.0 Cloudflare Worker.dev Online</h2>
</body>
</html>
"""

RESULTS_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Results for {{ query }}</title>
    <style>
        body { font-family: system-ui, sans-serif; background: #121218; color: #fff; margin: 0; padding: 20px; }
        .wrap { max-width: 760px; margin: 0 auto; }
        .top { display: flex; gap: 10px; align-items: center; margin-bottom: 18px; }
        .top a { color: #a29bfe; text-decoration: none; font-weight: 600; }
        form { display: flex; flex: 1; gap: 8px; }
        input[type="text"] { flex: 1; padding: 8px 12px; border-radius: 6px; border: 1px solid #444; background: #2a2a36; color: #fff; font-size: 14px; }
        input[type="submit"] { padding: 8px 14px; border: none; border-radius: 6px; background: #6c5ce7; color: #fff; font-weight: 600; cursor: pointer; }
        .item { background: #1e1e28; padding: 14px; border-radius: 8px; margin-bottom: 12px; border: 1px solid #2f2f3d; }
        .item a.main { color: #74b9ff; font-size: 17px; font-weight: 600; text-decoration: none; }
        .item a.main:hover { text-decoration: underline; }
        .item a.reader { color: #00b894; font-size: 13px; margin-left: 8px; text-decoration: none; }
        .item p { color: #b2bec3; margin: 6px 0 0; font-size: 14px; }
    </style>
</head>
<body>
    <div class="wrap">
        <div class="top">
            <a href="/">Home</a>
            <form action="/search" method="get">
                <input type="text" name="q" value="{{ query }}" required>
                <input type="submit" value="Search">
            </form>
        </div>
        {% if error %}
            <p style="color:#ff7675;">{{ error }}</p>
        {% endif %}
        {% for r in results %}
            <div class="item">
                <a class="main" href="{{ worker_url }}/?url={{ r.href | urlencode }}">{{ r.title }}</a>
                <a class="reader" href="/read?url={{ r.href | urlencode }}">[Reader Mode]</a>
                <p>{{ r.body }}</p>
            </div>
        {% endfor %}
    </div>
</body>
</html>
"""

READER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <style>
        body { font-family: system-ui, sans-serif; background: #121218; color: #dfe6e9; margin: 0; padding: 24px; line-height: 1.6; }
        .wrap { max-width: 740px; margin: 0 auto; }
        .nav { margin-bottom: 16px; }
        .nav a { color: #a29bfe; text-decoration: none; margin-right: 14px; font-weight: 600; }
        h1 { color: #fff; }
        img { max-width: 100%; height: auto; }
        a { color: #74b9ff; }
    </style>
</head>
<body>
    <div class="wrap">
        <div class="nav">
            <a href="javascript:history.back()">Back</a>
            <a href="{{ worker_url }}/?url={{ url | urlencode }}">Open Full Page (Proxy)</a>
        </div>
        <hr style="border-color:#333;">
        <h1>{{ title }}</h1>
        <div>{{ content | safe }}</div>
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HOME_HTML)

@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return render_template_string(HOME_HTML)
    results = []
    error = None
    try:
        results = list(DDGS().text(query, max_results=10))
    except Exception as e:
        error = f"Search temporarily rate-limited: {e}"
    return render_template_string(
        RESULTS_HTML,
        query=query,
        results=results,
        error=error,
        worker_url=WORKER_URL
    )

@app.route("/read")
def read():
    url = request.args.get("url", "")
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        doc = Document(response.text)
        return render_template_string(
            READER_HTML,
            title=doc.title(),
            content=doc.summary(),
            url=url,
            worker_url=WORKER_URL
        )
    except Exception as e:
        return render_template_string(
            READER_HTML,
            title="Could not load page",
            content=f"<p>Error fetching page: {e}</p>",
            url=url,
            worker_url=WORKER_URL
        )

if __name__ == "__main__":
    app.run(debug=True)
