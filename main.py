import os
import asyncio
from typing import Dict, Any
from dotenv import load_dotenv, set_key, find_dotenv
from browser_use import Agent
from browser_use.browser import browser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
import logging
import threading
from gradio_interface import create_gradio_interface

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
dotenv_path = find_dotenv()
if not dotenv_path:
    with open('.env', 'w') as f:
        f.write('')
    dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

Browser = browser.Browser
BrowserContext = browser.BrowserContext

class LLMManager:
    """Manages multiple LLM providers"""

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
    def get_llm(cls, model_id: str):
        """Initialize and return LLM instance"""
        if model_id not in cls.MODELS:
            raise ValueError(f"Invalid model ID: {model_id}")

        config = cls.MODELS[model_id]
        api_key = os.getenv(config["key_env"])

        if not api_key:
            raise ValueError(f"No API key found for {config['name']}")

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
    def list_models(cls):
        """Display available models and their status"""
        print("\nAvailable Models:")
        print("================")
        for id, model in cls.MODELS.items():
            key_status = "✅" if os.getenv(model["key_env"]) else "❌"
            print(f"{id}. {model['name']} ({model['provider']}) {key_status}")

    @classmethod
    def manage_api_keys(cls):
        """Manage API keys for all models"""
        while True:
            print("\nAPI Key Management")
            print("=================")
            cls.list_models()
            print("\nOptions:")
            print("1. Add/Update API Key")
            print("2. Remove API Key")
            print("3. Back to Main Menu")

            choice = input("\nSelect an option (1-3): ").strip()

            if choice == "1":
                cls.add_update_api_key()
            elif choice == "2":
                cls.remove_api_key()
            elif choice == "3":
                break
            else:
                print("Invalid choice")

    @classmethod
    def add_update_api_key(cls):
        """Add or update an API key"""
        cls.list_models()
        model_id = input("\nSelect model number to add/update API key: ").strip()

        if model_id not in cls.MODELS:
            print("Invalid model selection")
            return

        model = cls.MODELS[model_id]
        current_key = os.getenv(model["key_env"])

        print(f"\nCurrent API key for {model['name']}: {'*' * 8 if current_key else 'Not set'}")
        new_key = input(f"Enter new API key for {model['name']} (press Enter to keep current): ").strip()

        if new_key:
            try:
                set_key(dotenv_path, model["key_env"], new_key)
                load_dotenv(dotenv_path)
                print(f"\nAPI key for {model['name']} updated successfully")
            except Exception as e:
                print(f"Error updating API key: {str(e)}")
        else:
            print("No changes made")

    @classmethod
    def remove_api_key(cls):
        """Remove an API key"""
        cls.list_models()
        model_id = input("\nSelect model number to remove API key: ").strip()

        if model_id not in cls.MODELS:
            print("Invalid model selection")
            return

        model = cls.MODELS[model_id]
        if os.getenv(model["key_env"]):
            try:
                set_key(dotenv_path, model["key_env"], "")
                load_dotenv(dotenv_path)
                print(f"\nAPI key for {model['name']} removed successfully")
            except Exception as e:
                print(f"Error removing API key: {str(e)}")
        else:
            print(f"No API key set for {model['name']}")

class BrowserAutomation:
    def __init__(self):
        self.browser: Browser = None
        self.context: BrowserContext = None

    async def initialize(self):
        """Initialize browser and context"""
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
        """Clean up browser resources"""
        try:
            if self.context:
                await self.context.close()
                self.context = None
            if self.browser:
                await self.browser.close()
                self.browser = None
            logger.info("Browser resources cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

    async def run_task(self, task: str, model_id: str):
        """Execute a browser automation task"""
        try:
            await self.initialize()
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
        finally:
            await self.cleanup()

async def main_menu():
    """Main program loop"""
    automation = BrowserAutomation()

    try:
        while True:
            print("\nBrowser Automation Menu")
            print("=====================")
            print("1. Run Task")
            print("2. List Models")
            print("3. Manage API Keys")
            print("4. Exit")

            choice = input("\nSelect an option (1-4): ").strip()

            if choice == "1":
                LLMManager.list_models()
                model_id = input("\nSelect model number: ").strip()

                if model_id not in LLMManager.MODELS:
                    print("Invalid model selection")
                    continue

                if not os.getenv(LLMManager.MODELS[model_id]["key_env"]):
                    print(f"\nNo API key set for {LLMManager.MODELS[model_id]['name']}.")
                    print("Please set the API key first using the 'Manage API Keys' option.")
                    continue

                task = input("\nEnter your task: ").strip()
                if not task:
                    print("Task cannot be empty")
                    continue

                try:
                    await automation.run_task(task, model_id)
                except Exception as e:
                    print(f"Error executing task: {str(e)}")

            elif choice == "2":
                LLMManager.list_models()

            elif choice == "3":
                LLMManager.manage_api_keys()

            elif choice == "4":
                print("Exiting program...")
                break

            else:
                print("Invalid choice. Please select 1-4.")

    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    finally:
        await automation.cleanup()

def main():
    """Entry point"""
    try:
        print("Starting Browser Automation System...")

        # Create instances of required classes
        automation = BrowserAutomation()

        # Create and start Gradio interface in a separate thread
        demo = create_gradio_interface(LLMManager, automation)
        gradio_thread = threading.Thread(
            target=lambda: demo.launch(server_name="0.0.0.0", server_port=7860, share=True),
            daemon=True
        )
        gradio_thread.start()

        # Run the terminal interface
        asyncio.run(main_menu())

        print("Program terminated successfully")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        print("Program terminated due to an error")

if __name__ == "__main__":
    main()