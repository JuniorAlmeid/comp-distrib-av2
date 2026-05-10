import os, redis, requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify

app = Flask(__name__)
redis_url = os.environ.get('REDIS_URL')
cache = redis.from_url(redis_url) if redis_url else None

@app.route('/api/links')
def links():
    url = request.args.get('url')
    if cache:
        try:
            cached = cache.get(url)
            if cached: return cached
        except: pass
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        links = [a.get('href') for a in soup.find_all('a') if a.get('href')]
        result = jsonify({"url": url, "links": links})
        if cache:
            try: cache.set(url, result.get_data(), ex=300)
            except: pass
        return result
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
