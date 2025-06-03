from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Test route first
@app.route('/test')
def test():
    return "Backend is working"

# API health
@app.route('/api/health')  
def health():
    return jsonify({"status": "working"})

# Frontend - check if files exist
@app.route('/')
def home():
    frontend_dir = Path(__file__).parent / "frontend" / "dist"
    index_path = frontend_dir / "index.html"
    
    if index_path.exists():
        return send_from_directory(frontend_dir, 'index.html')
    else:
        return f"""
        <h1>VALIS Backend Running</h1>
        <p>Frontend path: {frontend_dir}</p>
        <p>Index exists: {index_path.exists()}</p>
        <p>Test: <a href="/test">/test</a></p>
        <p>API: <a href="/api/health">/api/health</a></p>
        """

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=3001, debug=True)
