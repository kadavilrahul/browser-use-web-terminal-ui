#!/bin/bash

# Exit on any error
set -e

echo "Starting browser automation tool..."

# Kill any process using port 7860
echo "Killing any process using port 7860..."
kill -9 $(lsof -t -i :7860) 2>/dev/null || true

# 1. Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup-debian.sh first..."
    bash setup-debian.sh
else
    # Activate virtual environment
    echo "Activating Python virtual environment..."
    source venv/bin/activate

    # Verify virtual environment
    PYTHON_PATH=$(which python3)
    if [[ $PYTHON_PATH != *"venv"* ]]; then
        echo "Error: Virtual environment not activated correctly"
        exit 1
    fi
    echo "Virtual environment activated successfully at: $PYTHON_PATH"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "Created .env file. Please edit it to add your API keys."
    else
        echo "Error: .env.example not found. Please run setup-debian.sh first."
        exit 1
    fi
fi

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Run the main application
echo "Starting the application..."
python3 main.py
