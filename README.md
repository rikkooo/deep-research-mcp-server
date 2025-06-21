# Deep Research MCP Server

This project provides a simple MCP (Model-as-a-Component-Provider) server that uses the OpenRouter API to perform deep research queries using Perplexity's online models.

## Prerequisites

- Docker
- An OpenRouter API Key

## How to Build and Run

1.  **Build the Docker image:**

    ```bash
    docker build -t deep-research-mcp-server .
    ```

2.  **Run the Docker container:**

    Replace `your_open_router_api_key` with your actual OpenRouter API key.

    ```bash
    docker run -d -p 8080:8080 -e OPENROUTER_API_KEY=your_open_router_api_key --name deep-research-server deep-research-mcp-server
    ```

## How to Use

Once the container is running, you can send a `POST` request to the `/deep_research` endpoint with a JSON payload containing your query.

**Example using `curl`:**

```bash
cURL -X POST -H "Content-Type: application/json" -d '{"query": "What are the latest advancements in AI?"}' http://localhost:8080/deep_research
```

The server will then contact the OpenRouter API and stream back the response from the Perplexity model.

## How to Integrate with a Code App (WindSurf, RooCode, etc.)

To integrate the Deep Research MCP Server with your code application, you can use the provided `npx` command. This allows you to easily call the server from your terminal or from within your application's scripts.

### Installation

First, install the client package globally using `npm`:

```bash
npm install -g .
```

### Usage

Once the package is installed, you can use the `deep-research` command followed by your query:

```bash
deep-research "What are the latest advancements in AI?"
```

This will send the query to the running MCP server and print the response to the console.

## How to Run Locally (for testing)

1.  **Create and activate a virtual environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Set the OpenRouter API Key:**

    Replace `your_open_router_api_key` with your actual key.

    ```bash
    export OPENROUTER_API_KEY=your_open_router_api_key
    ```

4.  **Run the application:**

    ```bash
    python app.py
    ```
