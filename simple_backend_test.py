#!/usr/bin/env python3
"""
Simple Backend Test
Minimal Flask app to test pipeline integration
"""

import sys
from pathlib import Path
from flask import Flask, request, jsonify

# Add VALIS root to path
sys.path.append(str(Path(__file__).parent))

from valis_inference_pipeline import VALISInferencePipeline

app = Flask(__name__)

# Initialize pipeline
pipeline = VALISInferencePipeline()
print("Pipeline initialized successfully")

@app.route('/test', methods=['POST'])
def test_chat():
    """Simple chat test endpoint"""
    try:
        data = request.get_json()
        message = data.get('message', 'Hello')
        
        print(f"Received message: {message}")
        
        # Call pipeline directly
        result = pipeline.run_memory_aware_chat(
            persona_id="marty",
            client_id="test_client",
            user_message=message,
            session_id="test_session"
        )
        
        print(f"Pipeline result: {result}")
        
        return jsonify({
            "success": result.get("success", False),
            "response": result.get("response", "No response"),
            "provider": result.get("provider", "Unknown"),
            "memory_layers": len(result.get("memory_used", {}))
        })
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("Starting simple backend test on port 3002")
    app.run(host='127.0.0.1', port=3002, debug=False)
