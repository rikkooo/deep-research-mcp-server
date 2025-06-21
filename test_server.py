import requests
import json
import os

def test_deep_research_endpoint():
    # Assuming the server is running on 0.0.0.0:8080
    # and accessed via the browser_preview proxy at 127.0.0.1:43247
    # In a real test scenario, you might run the server in a separate process
    # and get its actual port.
    url = "http://127.0.0.1:43247/deep_research"
    headers = {"Content-Type": "application/json"}
    payload = {"query": "What is the capital of Canada?"}

    print(f"Sending test request to {url} with query: {payload['query']}")

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), stream=True, timeout=30)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

        full_response_content = ""
        for chunk in response.iter_content(chunk_size=None):
            if chunk:
                full_response_content += chunk.decode('utf-8')

        print("Received response (partial view for brevity):")
        print(full_response_content[:500]) # Print first 500 characters

        # Basic assertion: check if the response contains expected text
        # This is a very simple check, more robust tests would parse SSE and JSON
        assert "Ottawa" in full_response_content or "capital of Canada is" in full_response_content, "Response does not contain expected answer for 'capital of Canada'"
        print("\nTest passed: Server returned a response containing 'Ottawa' or 'capital of Canada is'.")

    except requests.exceptions.ConnectionError as e:
        print(f"Test failed: Could not connect to the server. Is it running? Error: {e}")
        print("Please ensure the server is running and accessible at http://127.0.0.1:43247")
    except requests.exceptions.Timeout as e:
        print(f"Test failed: Request timed out. Error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Test failed: An error occurred during the request: {e}")
    except AssertionError as e:
        print(f"Test failed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    test_deep_research_endpoint()
