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

# 6. Create .env file and .gitignore
echo "Setting up environment files..."
echo "# API Keys Configuration" > .env.example
echo "GOOGLE_API_KEY=your_google_api_key_here" >> .env.example
echo "ANTHROPIC_API_KEY=your_anthropic_api_key_here" >> .env.example
echo "OPENAI_API_KEY=your_openai_api_key_here" >> .env.example

# Create .env file
cp .env.example .env

# Add .env to .gitignore
if [ ! -f ".gitignore" ]; then
    touch .gitignore
fi
if ! grep -q "^.env$" .gitignore; then
    echo ".env" >> .gitignore
fi

# 7. Collect API keys
echo -e "\nAPI Key Setup"
echo "You can get API keys from:"
echo "- Google API Key (Gemini): https://aistudio.google.com/"
echo "- Anthropic API Key (Claude): https://www.anthropic.com/api"
echo "- OpenAI API Key (GPT-4): https://platform.openai.com/api-keys"

read -p "Would you like to enter API keys now? (y/n): " setup_keys

if [ "$setup_keys" = "y" ]; then
    read -p "Enter GOOGLE_API_KEY (press Enter to skip): " google_key
    read -p "Enter ANTHROPIC_API_KEY (press Enter to skip): " anthropic_key
    read -p "Enter OPENAI_API_KEY (press Enter to skip): " openai_key

    if [ -n "$google_key" ]; then
        sed -i "s/^GOOGLE_API_KEY=.*$/GOOGLE_API_KEY=$google_key/" .env
    fi
    if [ -n "$anthropic_key" ]; then
        sed -i "s/^ANTHROPIC_API_KEY=.*$/ANTHROPIC_API_KEY=$anthropic_key/" .env
    fi
    if [ -n "$openai_key" ]; then
        sed -i "s/^OPENAI_API_KEY=.*$/OPENAI_API_KEY=$openai_key/" .env
    fi
    echo "API keys have been saved to .env file"
else
    echo "You can set up API keys later by editing the .env file"
fi

echo "Setup completed successfully!"
echo "To start the application, run: bash run.sh"
