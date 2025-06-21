import os
import requests
import json
import logging
from flask import Flask, request, jsonify

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

@app.route('/deep_research', methods=['POST'])
def deep_research():
    logging.info("Received request for /deep_research")
    data = request.get_json()
    query = data.get('query')
    logging.info(f"Received query: {query}")

    if not query:
        logging.error("Query not provided in request")
        return jsonify({'error': 'Query not provided'}), 400

    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        logging.error("OPENROUTER_API_KEY not set")
        return jsonify({'error': 'OPENROUTER_API_KEY not set'}), 500

    request_payload = {
        "model": "perplexity/llama-3.1-sonar-large-128k-online",
        "messages": [
            {"role": "user", "content": query}
        ]
    }
    
    logging.info(f"Sending request to OpenRouter with payload: {json.dumps(request_payload)}")

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {openrouter_api_key}",
            },
            data=json.dumps(request_payload)
        )

        logging.info(f"Received response from OpenRouter. Status code: {response.status_code}")
        logging.info(f"Response body: {response.text}")

        response.raise_for_status()  # Raise an exception for bad status codes

        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while calling OpenRouter API: {e}")
        return jsonify({'error': 'Failed to communicate with OpenRouter API'}), 502

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
