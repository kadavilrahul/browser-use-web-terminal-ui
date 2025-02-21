# Browser Automation with AI

- A minimal browser automation setup that integrates AI models
- It takes user input and executes tasks on a Chromium browser
- User can input tasks via terminal or Gradio web interface
- Repeat tasks can be entered in alredy open browser session
- New tasks have have context of previous task

Note: This is simplified and modified version of the original code: https://github.com/browser-use/browser-use

## Modifications and improvement done
- The tool will be ready to use by running three commands on terminal
- Made it user friendly by adding user inputs on terminal for all the tasks
- Use of terminal and web interface for input and output

## System Requirements
- Ubuntu Linux with GUI (GUI needed for browser access)
- Python 3.x
- Internet connection
- Tested on Linux Ubuntu 24.04
- If you are working on a remote Linux headless machine then you will need a GUI and remote desktop connection to access browser. You can install Chrome remote desktop on a remote Ubuntu machine using this repo https://github.com/kadavilrahul/chrome_remote_desktop

## Installation for Linux

1. Clone the repository:
```bash
git clone https://github.com/kadavilrahul/browser-use-web-terminal-ui.git && cd browser-use-web-terminal-ui
```

2. Run the setup script:
```bash
bash setup-debian.sh
```

3. Start the application (make sure your are in right folder in terminal):

Using run script (recommended):
```bash
bash run.sh
```

Rerun script If port is blocked:
```bash
bash rerun.sh
```

Rerun on headless mode:
```bash
bash headless.sh
```

4. Example tasks:
```
Go to wordpress order section of xxxx.com, ID:xxxx Password:xxxx and search for latest orders
```
```
Login to GitHub with username:xxx password:xxx and check notifications
```
## Installation for Windows (Currently only terminal UI works for windows)

1. Clone the repository:
```
git clone https://github.com/kadavilrahul/browser-use-web-terminal-ui.git; cd browser-use-web-terminal-ui
```
2. Install Python 3.x: Make sure Python is added to your PATH.
python --version

3. Create and activate virtual environment:
```
python -m venv venv; .\venv\Scripts\activate
```
5. Install the dependencies:
```
pip install -r requirements.txt
```
6. Install Playwright browsers:

```
python -m playwright install
```
```
python -m playwright install-deps
```
7. Set the API keys as environment variables.

8. Run the application:
```
python main.py
```

If port gets blocked, use the `rerun.bat` file to restart the application without closing the browser.

Create a `run.bat` file with the following content:

```batch
@echo off
echo Starting browser automation tool...
echo Killing any process using port 7860...
taskkill /F /FI "TCP eq 7860"
echo Activating Python virtual environment...
call venv\Scripts\activate
echo Starting the application...
python main.py
```
Run the `run.bat` file.

The `run.bat` script already includes the logic to kill any process using port 7860.

9. Exit the virtual environment:
```
deactivate
```

I will now attempt completion.
## Files

### Main Files
- `main.py`: Main application script
- `setup-debian.sh`: Script for installing dependencies and first-time configuration
- `requirements.txt`: Python package dependencies

### Configuration Files
- `.env`: Environment file for storing API keys and configuration
- `.gitignore`: Git ignore rules
- `README.md`: This documentation file

## The run.sh script will
- Check and activate virtual environment
- Verify environment setup
- Start the application automatically

# The setup-debian.sh script will:
- Create Python virtual environment
- Install all required packages
- Set up API key configuration
- Install browser dependencies

# You'll need API keys:
- Google Gemini API key: https://aistudio.google.com/apikey
- Anthropic Claude API key: https://www.anthropic.com/api
- OpenAI API key: https://platform.openai.com/api-keys
Enter them during setup or add them later to the `.env` file

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

Note:
1. This version has web UI with gradio
2. main.py is running well with gradio
3. Check updated library https://pypi.org/project/browser-use/
4. Use any IDE with AI support to modify code as per your use.
5. Modify lines 55, 62 and 69 in main.py to change the LLM model names.

