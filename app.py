import os
import requests
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/deep_research', methods=['POST'])
def deep_research():
    data = request.get_json()
    query = data.get('query')

    if not query:
        return jsonify({'error': 'Query not provided'}), 400

    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        return jsonify({'error': 'OPENROUTER_API_KEY not set'}), 500

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {openrouter_api_key}",
        },
        data=json.dumps({
            "model": "google/gemini-flash-1.5",
            "messages": [
                {"role": "user", "content": query}
            ]
        })
    )

    return jsonify(response.json()), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
