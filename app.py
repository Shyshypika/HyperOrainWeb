from flask import Flask, request, render_template_string
from duckduckgo_search import DDGS
from readability import Document
import requests

app = Flask(__name__)

# Simple HTML template that works on any browser
HOME_HTML = """
<!DOCTYPE html>
<html>
<head><title>RetroSearch</title></head>
<body>
    <center>
        <h1>RetroSearch</h1>
        <form action="/search" method="get">
            <input type="text" name="q" size="40" required>
            <input type="submit" value="Search">
        </form>
    </center>
</body>
</html>
"""

RESULTS_HTML = """
<!DOCTYPE html>
<html>
<head><title>Results for {{ query }}</title></head>
<body>
    <a href="/">Home</a> | <b>Results for: {{ query }}</b>
    <hr>
    {% for r in results %}
        <p>
            <a href="/read?url={{ r.href }}">{{ r.title }}</a><br>
            <small>{{ r.body }}</small>
        </p>
    {% endfor %}
</body>
</html>
"""

READER_HTML = """
<!DOCTYPE html>
<html>
<head><title>{{ title }}</title></head>
<body>
    <a href="javascript:history.back()">Back</a> | <a href="{{ url }}">Original Page</a>
    <hr>
    <h1>{{ title }}</h1>
    <div>{{ content | safe }}</div>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HOME_HTML)

@app.route("/search")
def search():
    query = request.args.get("q", "")
    results = DDGS().text(query, max_results=10)
    return render_template_string(RESULTS_HTML, query=query, results=results)

@app.route("/read")
def read():
    url = request.args.get("url", "")
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=10)
    doc = Document(response.text)
    return render_template_string(READER_HTML, title=doc.title(), content=doc.summary(), url=url)

if __name__ == "__main__":
    app.run(debug=True)
