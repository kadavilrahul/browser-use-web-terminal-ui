#!/bin/bash

# Exit on any error
set -e

echo "Starting setup process..."

# 1. Update system and install dependencies
echo "Installing system dependencies..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# 2. Create and activate virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 3. Verify virtual environment
PYTHON_PATH=$(which python3)
if [[ $PYTHON_PATH != *"venv"* ]]; then
    echo "Error: Virtual environment not activated correctly"
    exit 1
fi
echo "Virtual environment activated successfully at: $PYTHON_PATH"

# 4. Install Python packages
echo "Installing Python packages..."
python3 -m pip install -r requirements.txt

# 5. Install Playwright and browsers
echo "Installing Playwright and browsers..."
python3 -m playwright install
python3 -m playwright install-deps

# 6. Create .env file
echo "Setting up environment file..."
echo "# API Keys Configuration" > .env

# 7. Collect API key
echo "Please enter your API key."
echo "Google API Key (for Gemini model) - Get it from https://aistudio.google.com/"
read -p "Enter GOOGLE_API_KEY: " api_key

if [ -n "$api_key" ]; then
    echo "GOOGLE_API_KEY=$api_key" >> .env
    echo "API key has been saved to .env file"
else
    echo "No API key provided. You can add it later by editing .env file"
fi

# 8. Display model selection menu
echo -e "\nAvailable Models:"
echo "1. Gemini 2.0 Flash Exp (main-gemini-2.0-flash-exp.py)"
echo "2. Gemini 2.0 Flash (gemini-2.0-flash.py)"
echo "3. Gemini 1.5 Flash (gemini-1.5-flash.py)"
echo "4. Gemini 1.5 Flash 8B (gemini-1.5-flash-8b.py)"
echo "5. Gemini 1.5 Pro (gemini-1.5-pro.py)"
echo "6. Gemini 1.0 Pro (gemini-1.0-pro.py)"
echo "7. Gemini 2.0 Flash Thinking Exp (gemini-2.0-flash-thinking-exp-01-21.py)"
echo "8. Gemini Exp 1206 (gemini-exp-1206.py)"

while true; do
    read -p "Select a model (1-8): " model_choice
    case $model_choice in
        1) model_file="main-gemini-2.0-flash-exp.py" ; break ;;
        2) model_file="gemini-2.0-flash.py" ; break ;;
        3) model_file="gemini-1.5-flash.py" ; break ;;
        4) model_file="gemini-1.5-flash-8b.py" ; break ;;
        5) model_file="gemini-1.5-pro.py" ; break ;;
        6) model_file="gemini-1.0-pro.py" ; break ;;
        7) model_file="gemini-2.0-flash-thinking-exp-01-21.py" ; break ;;
        8) model_file="gemini-exp-1206.py" ; break ;;
        *) echo "Invalid choice. Please select a number between 1 and 8." ;;
    esac
done

# 9. Verify the selected model file exists
echo "Checking for the selected model script..."
if [ ! -f "$model_file" ]; then
    echo "Error: $model_file not found!"
    exit 1
fi

# 10. Make the script executable
chmod +x "$model_file"

echo "Setup completed successfully!"
echo "Starting the browser automation tool with $model_file..."
python3 "$model_file"
