# Browser Automation with Gemini AI

A streamlined browser automation tool that uses Google's Gemini AI to execute web-based tasks through natural language commands.

## System Requirements
- Ubuntu Linux with GUI (GUI needed for browser access)
- Python 3.x
- Internet connection

## Features
- Natural language task execution
- Automated browser control
- API key management
- Task recording (saves as GIF)
- Persistent browser session between tasks
- Multiple Gemini model support

## Available Models

The tool supports various Gemini models:
1. Gemini 2.0 Flash Exp (Default)
2. Gemini 2.0 Flash
3. Gemini 1.5 Flash
4. Gemini 1.5 Flash 8B
5. Gemini 1.5 Pro
6. Gemini 1.0 Pro
7. Gemini 2.0 Flash Thinking Exp
8. Gemini Exp 1206

Each model has its own characteristics and capabilities. During setup, you'll be prompted to choose which model you want to use.

## Installation

1. Clone the repository:
```bash
git clone [your-repository-url]
cd [repository-name]
```

2. Run the setup script:
```bash
bash setup-debian.sh
```

3. When prompted, select your preferred Gemini model (1-8)

## Configuration

You'll need a Google Gemini API key:
1. Get your free API key from: https://aistudio.google.com/apikey
2. Enter it during setup or add it later to the `.env` file

## Usage

1. Initial Setup and Run(This will install all dependencies and run your selected model):
```bash
bash setup-debian.sh
```

2. Subsequent Runs(Use this for all runs after the initial setup):
```bash
bash rerun.sh
```

3. Example tasks:
```
Go to wordpress order section of xxxx.com, ID:xxxx Password:xxxx and search for latest orders
```
```
Login to GitHub with username:xxx password:xxx and check notifications
```

## Switching Models

You can switch models in two ways:
1. Using rerun.sh (Recommended):
```bash
bash rerun.sh
```
Then select your desired model number when prompted.

2. Using setup-debian.sh (Full reinstall):
```bash
bash setup-debian.sh
```
Use this only if you need to reinstall dependencies or reconfigure your setup.

## Files

### Main Files
- `setup-debian.sh`: Script for installing dependencies and first-time configuration
- `rerun.sh`: Script for running models after initial setup
- `requirements.txt`: Python package dependencies

### Model Files
- `main-gemini-2.0-flash-exp.py`: Default Gemini 2.0 Flash Experimental model
- `gemini-2.0-flash.py`: Gemini 2.0 Flash model
- `gemini-1.5-flash.py`: Gemini 1.5 Flash model
- `gemini-1.5-flash-8b.py`: Gemini 1.5 Flash 8B model
- `gemini-1.5-pro.py`: Gemini 1.5 Pro model
- `gemini-1.0-pro.py`: Gemini 1.0 Pro model
- `gemini-2.0-flash-thinking-exp-01-21.py`: Gemini 2.0 Flash Thinking Experimental model
- `gemini-exp-1206.py`: Gemini Experimental 1206 model

### Configuration Files
- `.env`: Environment file for storing API keys and configuration
- `.gitignore`: Git ignore rules
- `README.md`: This documentation file

## Troubleshooting

1. Browser doesn't open:
```bash
playwright install-deps
```

2. API key issues:
- Check `.env` file format
- Ensure no spaces around '=' sign
- Verify key is active in Google AI Studio

## Key Dependencies
- browser-use: For browser automation
- langchain-google-genai: For Gemini AI integration
- python-dotenv: For API key management

## Recording
Task executions are automatically recorded and saved as `agent_history.gif` in the project directory.

## Notes
- Keep your API keys secure and never share them
- The browser stays open between tasks for efficiency
- Use 'exit' command to properly close the browser

For any issues or contributions, please open an issue in the repository.
