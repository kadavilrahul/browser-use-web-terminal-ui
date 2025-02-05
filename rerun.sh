#!/bin/bash

# Kill any process using port 7860
kill -9 $(lsof -t -i :7860) 2>/dev/null

# Activate the virtual environment
source venv/bin/activate

# Run the main Python script
python3 main.py
