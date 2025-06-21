# Deep Research MCP Server

This project provides a simple MCP (Model Context Protocol) server that uses the OpenRouter API to perform deep research queries using Perplexity's online models.

## Prerequisites

- Python 3.8+
- Node.js (optional, for npm commands)
- An OpenRouter API Key

## Setup and Running

### Initial Setup

To set up the project and install dependencies, run the `setup.sh` script:

```bash
./setup.sh
```

This script will:
- Create a `.env` file from `.env.example` if it doesn't exist
- Create a Python virtual environment if it doesn't exist
- Install all necessary Python dependencies

After running `setup.sh`, open the `.env` file and add your OpenRouter API key:

```
OPENROUTER_API_KEY=your_open_router_api_key
MODEL_NAME=perplexity/llama-3.1-sonar-large-128k-online
```

### Running the Server

You have two simple options to run the server:

#### Option 1: Using npm

```bash
npm start
```

#### Option 2: Using Python directly

```bash
source venv/bin/activate
python -m app
```

The server will be available at `http://localhost:5000`.

### MCP Client Integration

If you're using an MCP-compatible client, it will automatically detect and run the server using the configuration in `package.json`.

## MCP Server Configuration

This project follows the Model Context Protocol (MCP) specification. The MCP configuration is defined in the `package.json` file, making it easy for MCP clients to discover and use the server.

The MCP configuration is simple and standard:

```json
"mcp": {
  "servers": {
    "deep-research": {
      "command": "python",
      "args": [
        "-m",
        "app"
      ],
      "env": {
        "PATH": "${workspaceFolder}/venv/bin"
      },
      "description": "Deep Research MCP Server - Provides AI-powered research capabilities using OpenRouter API"
    }
  }
}
```

For clients that support MCP, simply point them to this project directory, and they will automatically detect and use the MCP configuration in `package.json`.

## API Reference

### `POST /deep_research`

Performs a deep research query using the configured model.

**Request Body:**

```json
{
  "query": "Your research query here"
}
```

**Response:**

The server will stream the response from the OpenRouter API. The response will be a series of server-sent events (SSE).
