#!/bin/bash

echo "==== Deep Research MCP Server Setup ===="

# Navigate to the project root
cd "$(dirname "$0")"

# Check if .env exists, if not, copy from .env.example
if [ ! -f .env ]; then
    echo "Creating .env from .env.example"
    cp .env.example .env
    echo "Please edit .env file to add your OPENROUTER_API_KEY"
else
    echo ".env already exists, skipping creation."
fi

# Create and activate virtual environment if it doesn't exist
if [ ! -d venv ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment and installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "==== Setup complete! ===="
echo "To run the MCP server, use one of the following commands:"
echo "1. npm start                  # Run the MCP server"
echo "2. python -m app              # Direct Python command"
echo ""
echo "MCP clients will automatically detect and use this server"
echo "The server will be available at http://localhost:8080"
