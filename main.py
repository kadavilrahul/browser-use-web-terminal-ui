import os
import asyncio
from typing import Dict, Any, Optional # Import Optional
from dotenv import load_dotenv, set_key, find_dotenv
from browser_use import Agent
from browser_use.browser import browser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
import logging
import threading
from gradio_interface import create_gradio_interface
from filelock import FileLock # Import FileLock

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def initialize_environment() -> str:
    """Initialize and return environment file path"""
    dotenv_path = find_dotenv()
    if not dotenv_path:
        with open('.env', 'w') as f:
            f.write('')
        dotenv_path = find_dotenv()
    return dotenv_path

# Load environment variables
dotenv_path = initialize_environment()
load_dotenv(dotenv_path)

Browser = browser.Browser
BrowserContext = browser.BrowserContext

class LLMManager:
    """Manages multiple LLM providers with API key verification and management"""

    _env_lock = FileLock(".env.lock") # Initialize FileLock

    MODELS = {
        "1": {
            "name": "Gemini",
            "provider": "Google",
            "model": "gemini-2.0-flash-exp",
            "key_env": "GOOGLE_API_KEY",
            "class": ChatGoogleGenerativeAI
        },
        "2": {
            "name": "Claude",
            "provider": "Anthropic",
            "model": "claude-3-opus-20240229",
            "key_env": "ANTHROPIC_API_KEY",
            "class": ChatAnthropic
        },
        "3": {
            "name": "GPT-4",
            "provider": "OpenAI",
            "model": "gpt-4",
            "key_env": "OPENAI_API_KEY",
            "class": ChatOpenAI
        }
    }

    @classmethod
    def _validate_key_format(cls, provider: str, key: str) -> bool:
        """Validate API key format based on provider"""
        if not key:
            return False
        if provider == "Google":
            return key.startswith("AIzaSy")
        elif provider == "OpenAI":
            return key.startswith("sk-")
        elif provider == "Anthropic":
            return len(key) == 40 and key.isalnum()
        return False

    @classmethod
    def _mask_key(cls, key: str) -> str:
        """Securely mask API key for display"""
        if not key:
            return "Not set"
        return f"{key[:4]}...{key[-4:]}"

    @classmethod
    async def _update_env_safely(cls, key_env: str, new_key: str) -> bool:
        """Atomic environment updates with file locking"""
        with cls._env_lock:
            try:
                set_key(dotenv_path, key_env, new_key.strip()) # Sanitize input key
                load_dotenv(dotenv_path, override=True)
                return True
            except Exception as e:
                logger.error(f"Error updating environment: {str(e)}")
                return False

    @classmethod
    async def _revert_key_safely(cls, key_env: str, old_key: str) -> None:
        """Safely revert to previous key with validation"""
        if old_key and cls._validate_key_format(cls._get_provider(key_env), old_key):
            await cls._update_env_safely(key_env, old_key)
        else:
            await cls._update_env_safely(key_env, "") # Revert to empty if no valid old key

    @classmethod
    def _get_provider(cls, key_env: str) -> Optional[str]:
        """Get provider name from key_env"""
        for model in cls.MODELS.values():
            if model["key_env"] == key_env:
                return model["provider"]
        return None

    @classmethod
    async def verify_api_key(cls, model_id: str) -> tuple[bool, str]:
        """Verify API key with a test prompt and format validation"""
        try:
            config = cls.MODELS[model_id]
            api_key = os.getenv(config["key_env"])

            if not api_key:
                return False, "No API key found"

            if not cls._validate_key_format(config["provider"], api_key):
                return False, f"❌ Invalid {config['provider']} API key format"

            # Initialize LLM
            llm = None
            try:
                if config["provider"] == "Google":
                    llm = config["class"](
                        google_api_key=api_key,
                        model=config["model"],
                        temperature=0
                    )
                elif config["provider"] == "Anthropic":
                    llm = config["class"](
                        anthropic_api_key=api_key,
                        model=config["model"],
                        temperature=0
                    )
                else:  # OpenAI
                    llm = config["class"](
                        api_key=api_key,
                        model=config["model"],
                        temperature=0
                    )
            except Exception as e:
                logger.error(f"Error initializing LLM for verification: {e}")
                return False, f"❌ Error initializing LLM: {str(e)}"


            # Test prompt
            try:
                messages = [{"role": "user", "content": "Respond with exactly 'OK' and nothing else"}]
                response = await llm.ainvoke(messages)

                if "OK" in str(response.content):
                    return True, "✅ API key verified successfully"
                return False, "❌ API key verification failed: Unexpected response"

            except Exception as e:
                logger.error(f"API Key verification request failed: {e}")
                return False, f"❌ API key verification failed: {str(e)}"

        except Exception as e:
            logger.error(f"Error during key verification process: {e}")
            return False, f"❌ API key verification process error: {str(e)}"

    @classmethod
    def get_llm(cls, model_id: str):
        """Initialize and return LLM instance with error handling"""
        if model_id not in cls.MODELS:
            raise ValueError(f"Invalid model ID: {model_id}")

        config = cls.MODELS[model_id]
        api_key = os.getenv(config["key_env"])

        if not api_key:
            raise ValueError(f"No API key found for {config['name']}")

        if not cls._validate_key_format(config["provider"], api_key):
            raise ValueError(f"Invalid {config['provider']} API key format")


        try:
            if config["provider"] == "Google":
                return config["class"](
                    google_api_key=api_key,
                    model=config["model"]
                )
            elif config["provider"] == "Anthropic":
                return config["class"](
                    anthropic_api_key=api_key,
                    model=config["model"]
                )
            else:  # OpenAI
                return config["class"](
                    api_key=api_key,
                    model=config["model"]
                )
        except Exception as e:
            logger.error(f"Error initializing {config['name']}: {str(e)}")
            raise

    @classmethod
    async def list_models(cls):
        """Display available models and their status with detailed messages"""
        print("\nVerifying API keys...")
        model_statuses = {}

        for id, model in cls.MODELS.items():
            if os.getenv(model["key_env"]):
                is_valid, message = await cls.verify_api_key(id)
                model_statuses[id] = is_valid
                if not is_valid:
                    print(f"Warning: {model['name']} - {message}") # Detailed warning message
            else:
                model_statuses[id] = False

        print("\nAvailable AI Models:")
        print("----")
        for id, model in cls.MODELS.items():
            key_status = "✅" if model_statuses[id] else "❌"
            status_display = key_status if model_statuses[id] else "❌ (Key Missing/Invalid)" # More informative status
            print(f"{id}. {model['name']} ({model['provider']}) {status_display}")

        return model_statuses

    @classmethod
    async def manage_api_keys(cls):
        """Manage API keys for all models with improved UI"""
        while True:
            print("\n=== API Key Management ===")
            await cls.list_models()
            print("\nOptions:")
            print("1. Add/Update API Key")
            print("2. Remove API Key")
            print("3. Back to Main Menu")

            choice = input("\nSelect an option (1-3): ").strip()

            if choice == "1":
                await cls.add_update_api_key()
            elif choice == "2":
                await cls.remove_api_key()
            elif choice == "3":
                break
            else:
                print("❌ Invalid choice. Please select 1-3.")

    @classmethod
    async def add_update_api_key(cls):
        """Add or update an API key with validation and safe reversion"""
        model_statuses = await cls.list_models()
        model_id = input("\nSelect model number to add/update API key: ").strip()

        if model_id not in cls.MODELS:
            print("❌ Invalid model selection")
            return

        model = cls.MODELS[model_id]
        current_key = os.getenv(model["key_env"])

        print(f"\nCurrent API key for {model['name']}: {cls._mask_key(current_key)}")
        new_key = input(f"Enter new API key for {model['name']} (press Enter to keep current): ").strip()

        if new_key:
            if not cls._validate_key_format(model["provider"], new_key):
                print(f"❌ Invalid {model['provider']} API key format. Please check the format.")
                return

            try:
                # Store current key as backup before update
                current_key_backup = current_key

                if await cls._update_env_safely(model["key_env"], new_key):
                    print(f"\nTesting API key for {model['name']}...")
                    is_valid, message = await cls.verify_api_key(model_id)
                    print(message)

                    if not is_valid:
                        print(f"⚠️ Verification failed. Reverting to previous API key for {model['name']}.")
                        await cls._revert_key_safely(model["key_env"], current_key_backup) # Revert to backup
                    else:
                        print(f"✅ API key for {model['name']} updated and verified successfully.")
                else:
                    print(f"❌ Failed to update API key for {model['name']}.")

            except Exception as e:
                logger.error(f"Error in add_update_api_key: {e}")
                print(f"❌ Error updating API key: {str(e)}")
        else:
            print("ℹ️ No changes made to API key.")

    @classmethod
    async def remove_api_key(cls):
        """Remove an API key with confirmation"""
        await cls.list_models()
        model_id = input("\nSelect model number to remove API key: ").strip()

        if model_id not in cls.MODELS:
            print("❌ Invalid model selection")
            return

        model = cls.MODELS[model_id]
        if os.getenv(model["key_env"]):
            confirm_remove = input(f"⚠️ Are you sure you want to remove the API key for {model['name']}? (yes/no): ").strip().lower()
            if confirm_remove == 'yes':
                try:
                    if await cls._update_env_safely(model["key_env"], ""): # Set to empty string to remove
                        print(f"\n✅ API key for {model['name']} removed successfully.")
                    else:
                        print(f"❌ Failed to remove API key for {model['name']}.")
                except Exception as e:
                    logger.error(f"Error in remove_api_key: {e}")
                    print(f"❌ Error removing API key: {str(e)}")
            else:
                print("ℹ️ API key removal cancelled.")
        else:
            print(f"ℹ️ No API key set for {model['name']}")


class BrowserAutomation:
    def __init__(self):
        self.browser: Browser = None
        self.context: BrowserContext = None
        self._init_lock = threading.Lock() # Lock for browser initialization

    async def initialize(self):
        """Initialize browser and context with thread lock to prevent race conditions"""
        with self._init_lock:
            if self.browser and self.context: # Check if already initialized
                return

            try:
                if not self.browser:
                    self.browser = Browser()
                if not self.context:
                    self.context = await self.browser.new_context()
                logger.info("Browser and context initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing browser: {str(e)}")
                raise

    async def cleanup(self):
        """Clean up browser resources safely"""
        try:
            if self.context:
                await self.context.close()
                self.context = None
            if self.browser:
                await self.browser.close()
                self.browser = None
            logger.info("Browser resources cleaned up")
        except Exception as e:
            logger.error(f"Error during browser cleanup: {str(e)}")

    async def run_task(self, task: str, model_id: str):
        """Execute a browser automation task"""
        try:
            await self.initialize() # Ensure browser is initialized

            llm = LLMManager.get_llm(model_id)

            agent = Agent(
                task=task,
                llm=llm,
                browser=self.browser,
                browser_context=self.context
            )

            logger.info(f"Starting task execution with {LLMManager.MODELS[model_id]['name']}")
            await agent.run()
            logger.info("Task completed successfully")

        except Exception as e:
            logger.error(f"Error during task execution: {str(e)}")
            raise

async def main_menu():
    """Main program loop for terminal interface"""
    automation = BrowserAutomation()

    try:
        while True:
            print("\n=== Browser Automation System ===")
            print("\nAvailable Actions:")
            print("1. Execute Browser Task")
            print("2. Manage API Keys")
            print("3. Exit")

            choice = input("\nSelect action (1-3): ").strip()

            if choice == "1":
                model_statuses = await LLMManager.list_models() # Get model statuses
                model_id = input("\nSelect AI model number (1-3): ").strip()

                if model_id not in LLMManager.MODELS:
                    print("\n❌ Invalid model selection. Please try again.")
                    continue

                if not model_statuses.get(model_id, False): # Check if key is valid from status
                    print(f"\n❌ Invalid or missing API key for {LLMManager.MODELS[model_id]['name']}")
                    print("Please set up your API key first using option 2")
                    continue

                print(f"\nUsing {LLMManager.MODELS[model_id]['name']} for task execution")
                print("\nExample tasks:")
                print("- Go to wordpress order section of website.com, login with ID:xxx Password:xxx")
                print("- Login to GitHub with username:xxx password:xxx and check notifications")

                task = input("\nEnter your task: ").strip()
                if not task:
                    print("\n❌ Task cannot be empty")
                    continue

                while True: # Loop for task continuation
                    try:
                        print("\nExecuting task...")
                        await automation.run_task(task, model_id)
                        print("\n✅ Task completed successfully")

                        another_task = input("Perform another task? (y/n): ").strip().lower()
                        if another_task == 'n':
                            break # Exit inner loop, back to main menu
                        elif another_task == 'y':
                            task = input("\nEnter your next task: ").strip() # Ask for next task
                            if not task:
                                print("\n❌ Task cannot be empty")
                                continue # Continue inner loop to ask for task again
                        else:
                            print("\n❌ Invalid input. Please enter 'y' or 'n'.")
                            continue # Continue inner loop to ask y/n again

                    except Exception as e:
                        print(f"\n❌ Error executing task: {str(e)}")
                        break # Exit inner loop on error

                if another_task == 'n': # Check if user chose 'n' to break outer loop as well if needed. In this case, no need as break in inner loop goes to main menu options.
                    pass # No action needed, will go back to main menu options

            elif choice == "2":
                await LLMManager.manage_api_keys()

            elif choice == "3":
                print("\nExiting program...")
                await automation.cleanup()
                break

            else:
                print("\n❌ Invalid choice. Please select 1-3.")

    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user")
        await automation.cleanup()
    except Exception as e:
        logger.error(f"Unexpected error in main_menu: {str(e)}")
        await automation.cleanup()

def main():
    """Entry point of the application"""
    try:
        print("Starting Browser Automation System...")

        # Create instances
        automation = BrowserAutomation()

        # Launch Gradio interface in a separate thread
        demo = create_gradio_interface(LLMManager, automation)
        gradio_thread = threading.Thread(
            target=lambda: demo.launch(server_name="0.0.0.0", server_port=7860, share=True),
            daemon=True
        )
        gradio_thread.start()

        # Run the terminal interface in the main thread
        asyncio.run(main_menu())

        print("Program terminated successfully")

    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}")
        print("Program terminated due to an error")

if __name__ == "__main__":
    main()