#!/usr/bin/env python3
from flask import Flask, jsonify
from flask_cors import CORS
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return """<!DOCTYPE html>
<html>
<head><title>VALIS System</title></head>
<body>
<h1>VALIS System Online</h1>
<p>Backend running successfully</p>
<h2>Test API:</h2>
<script>
fetch('/api/health').then(r=>r.json()).then(d=>document.getElementById('health').innerHTML=JSON.stringify(d,null,2));
</script>
<pre id="health">Loading...</pre>
</body>
</html>"""

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "message": "VALIS API working"})

if __name__ == "__main__":
    print("Starting VALIS on http://127.0.0.1:3001")
    app.run(host='127.0.0.1', port=3001, debug=False)
