#!/bin/bash

# Update package list and install xvfb
sudo apt-get update
sudo apt-get install -y xvfb


# Kill any process using port 7860
kill -9 $(lsof -t -i :7860) 2>/dev/null

# Activate the virtual environment
source venv/bin/activate

# Run the main Python script
xvfb-run -a python3 main.py
