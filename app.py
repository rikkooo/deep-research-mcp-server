import os
import requests
import json
import logging
import sys
from flask import Flask, request, jsonify, Response
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/deep_research', methods=['POST'])
def deep_research():
    logging.info("Received request for /deep_research")
    data = request.get_json()
    query = data.get('query')
    logging.info(f"Received query: {query}")

    if not query:
        logging.error("Query not provided in request")
        return jsonify({'error': 'Query not provided'}), 400

    openrouter_api_key = app.config['OPENROUTER_API_KEY']
    if not openrouter_api_key:
        logging.error("OPENROUTER_API_KEY not set")
        return jsonify({'error': 'OPENROUTER_API_KEY not set'}), 500

    # Allow model to be configurable, with a default
    model = app.config['MODEL_NAME']

    request_payload = {
        "model": model,
        "messages": [{"role": "user", "content": query}],
        "stream": True  # Enable streaming
    }
    
    logging.info(f"Sending streaming request to OpenRouter with payload: {json.dumps(request_payload)}")

    def generate():
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openrouter_api_key}",
                    "Content-Type": "application/json"
                },
                data=json.dumps(request_payload),
                stream=True,
                timeout=600  # 10-minute timeout
            )
            logging.info(f"Received response from OpenRouter. Status code: {response.status_code}")
            response.raise_for_status()

            # Stream the response line by line
            for line in response.iter_lines():
                if line:
                    yield line + b'\n'

        except requests.exceptions.RequestException as e:
            logging.error(f"An error occurred while calling OpenRouter API: {e}")
            error_message = json.dumps({'error': f'Failed to communicate with OpenRouter API: {e}'})
            yield f"data: {error_message}\n\n".encode('utf-8')

    # The content_type 'text/event-stream' is crucial for SSE
    return Response(generate(), content_type='text/event-stream')

# MCP server health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "ok",
        "version": "1.0.0",
        "name": "deep-research"
    })

# MCP server capabilities endpoint
@app.route('/capabilities', methods=['GET'])
def capabilities():
    return jsonify({
        "tools": [
            {
                "name": "deep_research",
                "description": "Performs deep research using OpenRouter API",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The research query to process"
                        }
                    },
                    "required": ["query"]
                }
            }
        ]
    })

def main():
    # When run as a module, start the server
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    main()
