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
            "model": "gemini-2.0-flash-exp",  # Changed to correct model name
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
    async def verify_api_key(cls, model_id: str) -> tuple[bool, str]:
        """Verify API key with a test prompt"""
        try:
            config = cls.MODELS[model_id]
            api_key = os.getenv(config["key_env"])

            if not api_key:
                return False, "No API key found"

            # Initialize LLM
            llm = None
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

            # Test prompt
            messages = [{"role": "user", "content": "Respond with exactly 'OK' and nothing else"}]
            response = await llm.ainvoke(messages)

            if "OK" in str(response.content):
                return True, "✅ API key verified successfully"
            return False, "❌ API key verification failed"

        except Exception as e:
            return False, f"❌ API key verification failed: {str(e)}"

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
    async def list_models(cls):
        """Display available models and their status"""
        print("\nVerifying API keys...")
        model_statuses = {}

        for id, model in cls.MODELS.items():
            if os.getenv(model["key_env"]):
                is_valid, message = await cls.verify_api_key(id)
                model_statuses[id] = is_valid
                if not is_valid:
                    print(f"Warning: {model['name']} - {message}")
            else:
                model_statuses[id] = False

        print("\nAvailable AI Models:")
        print("--------------------")
        for id, model in cls.MODELS.items():
            key_status = "✅" if model_statuses[id] else "❌"
            print(f"{id}. {model['name']} ({model['provider']}) {key_status}")

        return model_statuses

    @classmethod
    async def manage_api_keys(cls):
        """Manage API keys for all models"""
        while True:
            print("\nAPI Key Management")
            print("--------------------")
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
                print("❌ Invalid choice")

    @classmethod
    async def add_update_api_key(cls):
        """Add or update an API key"""
        model_statuses = await cls.list_models()
        model_id = input("\nSelect model number to add/update API key: ").strip()

        if model_id not in cls.MODELS:
            print("❌ Invalid model selection")
            return

        model = cls.MODELS[model_id]
        current_key = os.getenv(model["key_env"])

        print(f"\nCurrent API key for {model['name']}: {'*' * 8 if current_key else 'Not set'}")
        new_key = input(f"Enter new API key for {model['name']} (press Enter to keep current): ").strip()

        if new_key:
            try:
                set_key(dotenv_path, model["key_env"], new_key)
                load_dotenv(dotenv_path)
                print(f"\nTesting API key for {model['name']}...")
                is_valid, message = await cls.verify_api_key(model_id)
                print(message)
                if not is_valid:
                    # Revert the key if verification fails
                    if current_key:
                        set_key(dotenv_path, model["key_env"], current_key)
                    else:
                        set_key(dotenv_path, model["key_env"], "")
                    load_dotenv(dotenv_path)
            except Exception as e:
                print(f"❌ Error updating API key: {str(e)}")
        else:
            print("ℹ️ No changes made")

    @classmethod
    async def remove_api_key(cls):
        """Remove an API key"""
        await cls.list_models()
        model_id = input("\nSelect model number to remove API key: ").strip()

        if model_id not in cls.MODELS:
            print("❌ Invalid model selection")
            return

        model = cls.MODELS[model_id]
        if os.getenv(model["key_env"]):
            try:
                set_key(dotenv_path, model["key_env"], "")
                load_dotenv(dotenv_path)
                print(f"\n✅ API key for {model['name']} removed successfully")
            except Exception as e:
                print(f"❌ Error removing API key: {str(e)}")
        else:
            print(f"ℹ️ No API key set for {model['name']}")

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
            # Only initialize if browser is not already running
            if not self.browser or not self.context:
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

async def main_menu():
    """Main program loop"""
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
                # Display models with verified status
                model_statuses = await LLMManager.list_models()
                model_id = input("\nSelect AI model number (1-3): ").strip()

                if model_id not in LLMManager.MODELS:
                    print("\n❌ Invalid model selection. Please try again.")
                    continue

                if not model_statuses[model_id]:
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

                try:
                    print("\nExecuting task...")
                    await automation.run_task(task, model_id)
                    print("\n✅ Task completed successfully")
                except Exception as e:
                    print(f"\n❌ Error executing task: {str(e)}")

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
        logger.error(f"Unexpected error: {str(e)}")
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
