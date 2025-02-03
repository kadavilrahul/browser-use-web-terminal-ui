import os
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from browser_use import Agent
from browser_use.browser import browser
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

Browser = browser.Browser
BrowserContext = browser.BrowserContext

class APIManager:
    """Manages API key for Gemini model"""
    
    # File to store API key
    KEY_FILE = os.path.join(str(Path.home()), ".browser_use", "api_keys.json")
    
    # Gemini model configuration
    MODELS = {
        "1": {
            "model": "gemini-1.5-flash-8b",
            "name": "Gemini 1.5 Flash 8B",
            "provider": "Google",
            "key_name": "GOOGLE_API_KEY",
            "pricing": "Free",
            "test_prompt": "Say 'Hello' if you can hear me.",
            "max_tokens": 2048,
            "temperature": 0.7,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "stop": None
        }
    }
    
    @classmethod
    def _ensure_key_file(cls) -> None:
        os.makedirs(os.path.dirname(cls.KEY_FILE), exist_ok=True)
        if not os.path.exists(cls.KEY_FILE):
            with open(cls.KEY_FILE, "w") as f:
                json.dump({}, f)
    
    @classmethod
    def _load_keys(cls) -> Dict[str, str]:
        cls._ensure_key_file()
        try:
            with open(cls.KEY_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    
    @classmethod
    def _save_keys(cls, keys: Dict[str, str]) -> None:
        cls._ensure_key_file()
        with open(cls.KEY_FILE, "w") as f:
            json.dump(keys, f)
    
    @classmethod
    def add_key(cls, model_num: str, api_key: str) -> bool:
        if model_num != "1" or not api_key:
            return False
        keys = cls._load_keys()
        keys[model_num] = api_key
        try:
            cls._save_keys(keys)
            return True
        except Exception:
            return False
    
    @classmethod
    def remove_key(cls, model_num: str) -> bool:
        if model_num != "1":
            return False
        keys = cls._load_keys()
        if model_num in keys:
            del keys[model_num]
            try:
                cls._save_keys(keys)
                return True
            except Exception:
                return False
        return False
    
    @classmethod
    def get_key(cls, model_num: str) -> Optional[str]:
        if model_num != "1":
            return None
        env_key = os.getenv(cls.MODELS[model_num]["key_name"])
        if env_key and env_key.strip():
            return env_key.strip()
        keys = cls._load_keys()
        key = keys.get(model_num, "").strip()
        return key if key else None
    
    @classmethod
    def list_models(cls) -> None:
        print("\nAvailable Model:")
        print("===============")
        model = cls.MODELS["1"]
        key = cls.get_key("1")
        status = "✅" if key else "❌"
        print(f"1. {model['name']} - {model['provider']} ({model['pricing']}) {status}")

async def test_api_key():
    """Test if the Gemini API key works"""
    api_key = APIManager.get_key("1")
    if not api_key:
        print("No API key found for Gemini")
        return False
    try:
        llm = ChatGoogleGenerativeAI(
            model=APIManager.MODELS["1"]['model'],
            google_api_key=api_key
        )
        await llm.ainvoke(APIManager.MODELS["1"]['test_prompt'])
        return True
    except Exception as e:
        print(f"Error testing API key: {str(e)}")
        return False

async def prompt_for_api_key():
    """Prompt user to add an API key"""
    print("\nNo API key found. Please add your Google API key.")
    api_key = input("Enter Gemini API key: ").strip()
    
    if not api_key:
        print("❌ API key cannot be empty")
        return False
    
    try:
        llm = ChatGoogleGenerativeAI(
            model=APIManager.MODELS["1"]['model'],
            google_api_key=api_key
        )
        await llm.ainvoke("Test")
        
        if APIManager.add_key("1", api_key):
            print("✅ API key added successfully")
            return True
        else:
            print("❌ Failed to save API key")
            return False
    except Exception as e:
        print(f"❌ Invalid API key: {str(e)}")
        return False

async def manage_api_keys():
    """Manage API keys - add, remove, or list"""
    while True:
        print("\nAPI Key Management")
        print("=================")
        print("1. Add/Update API Key")
        print("2. Remove API Key") 
        print("3. List Status")
        print("4. Return to Main Menu")
        
        choice = input("\nSelect an option (1-4): ").strip()
        
        if choice == "1":
            await prompt_for_api_key()
        elif choice == "2":
            if APIManager.remove_key("1"):
                print("✅ API key removed")
            else:
                print("❌ No API key found")
        elif choice == "3":
            APIManager.list_models()
            input("\nPress Enter to continue...")
        elif choice == "4":
            break
        else:
            print("Invalid choice")

async def run_task(task: str, browser_instance=None, browser_context=None):
    """Run a single browser task"""
    try:
        api_key = APIManager.get_key("1")
        if not api_key:
            print("No API key found for Gemini")
            return browser_instance, browser_context
        
        if browser_instance is None:
            browser_instance = Browser()
        
        if browser_context is None:
            browser_context = await browser_instance.new_context()
        
        llm = ChatGoogleGenerativeAI(
            model=APIManager.MODELS["1"]['model'],
            google_api_key=api_key
        )
        
        agent = Agent(
            task=task,
            llm=llm,
            browser=browser_instance,
            browser_context=browser_context
        )
        await agent.run()
        
        return browser_instance, browser_context
        
    except Exception as e:
        print(f"Error: {str(e)}")
        if browser_context:
            await browser_context.close()
        if browser_instance:
            await browser_instance.close()
        return None, None

async def run_tasks():
    """Run browser tasks"""
    browser_instance = None
    browser_context = None
    
    try:
        while True:
            if not APIManager.get_key("1"):
                if not await prompt_for_api_key():
                    return
            
            if browser_instance is None:
                print("\nBrowser Automation Menu")
                print("=====================")
                print("1. Run Task")
                print("2. Manage API Keys")
                print("3. Exit")
                
                choice = input("\nSelect an option (1-3): ").strip()
                
                if choice == "2":
                    await manage_api_keys()
                    continue
                elif choice == "3":
                    break
                elif choice != "1":
                    print("Invalid choice")
                    continue
            
            task = input("\nEnter your task (or 'exit' to quit): ").strip()
            if not task:
                print("Task cannot be empty")
                continue
            elif task.lower() == 'exit':
                break
            
            browser_instance, browser_context = await run_task(
                task, 
                browser_instance, 
                browser_context
            )
            
            if browser_instance is None:
                continue
                
    finally:
        if browser_context:
            await browser_context.close()
        if browser_instance:
            await browser_instance.close()

async def main_async():
    """Main async function"""
    while True:
        try:
            await run_tasks()
            break
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            cont = input("\nRetry? (y/n): ").lower().strip()
            if cont != 'y':
                break

def main():
    """Main entry point"""
    asyncio.run(main_async())

if __name__ == "__main__":
    main()