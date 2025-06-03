from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "WORKING"

@app.route('/api/test')  
def test():
    return {"status": "ok"}

if __name__ == "__main__":
    print("Starting on 3002...")
    app.run(host='127.0.0.1', port=3002, debug=False)
