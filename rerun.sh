#!/bin/bash

# Exit on any error
set -e

echo "Starting browser automation tool..."

# 1. Activate virtual environment
echo "Activating Python virtual environment..."
source venv/bin/activate

# 2. Verify virtual environment
PYTHON_PATH=$(which python3)
if [[ $PYTHON_PATH != *"venv"* ]]; then
    echo "Error: Virtual environment not activated correctly"
    exit 1
fi
echo "Virtual environment activated successfully at: $PYTHON_PATH"

# 3. Display model selection menu
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

# 4. Verify the selected model file exists
echo "Checking for the selected model script..."
if [ ! -f "$model_file" ]; then
    echo "Error: $model_file not found!"
    exit 1
fi

echo "Starting the browser automation tool with $model_file..."
python3 "$model_file"
