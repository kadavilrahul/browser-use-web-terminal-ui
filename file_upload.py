import os
import asyncio
from pathlib import Path
import logging
from browser_use import Agent, Controller, ActionResult
from browser_use.browser.browser import Browser, BrowserConfig
from langchain_google_genai import ChatGoogleGenerativeAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
GOOGLE_API_KEY = "your_api_key"
PDF_PATH = "/path/to/your/file.pdf"
GITHUB_USERNAME = "username"
GITHUB_PASSWORD = "password"

# Initialize controller
controller = Controller()

@controller.action('Upload pdf to element')
async def upload_pdf(index: int, browser: Browser):
    """Upload PDF file to a specific element"""
    path = str(Path(PDF_PATH).absolute())
    dom_el = await browser.get_dom_element_by_index(index)

    if dom_el is None:
        return ActionResult(error=f'No element found at index {index}')

    file_upload_dom_el = dom_el.get_file_upload_element()

    if file_upload_dom_el is None:
        logger.info(f'No file upload element found at index {index}')
        return ActionResult(error=f'No file upload element found at index {index}')

    file_upload_el = await browser.get_locate_element(file_upload_dom_el)

    if file_upload_el is None:
        logger.info(f'No file upload element found at index {index}')
        return ActionResult(error=f'No file upload element found at index {index}')

    try:
        await file_upload_el.set_input_files(path)
        msg = f'Successfully uploaded file "{path}" to index {index}'
        logger.info(msg)
        return ActionResult(extracted_content=msg)
    except Exception as e:
        logger.debug(f'Error in set_input_files: {str(e)}')
        return ActionResult(error=f'Failed to upload file to index {index}')

class BrowserAutomation:
    def __init__(self):
        self.browser = None
        self.context = None

    async def initialize(self):
        """Initialize browser and context"""
        if not self.browser:
            browser_config = BrowserConfig(
                disable_security=True,
                headless=False  # Set to False to see the browser
            )
            self.browser = Browser(config=browser_config)
            self.context = await self.browser.new_context()
            logger.info("Browser and context initialized successfully")

    async def cleanup(self):
        """Clean up browser resources"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            logger.info("Browser resources cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

    async def upload_pdf_to_github(self):
        """Upload PDF to GitHub"""
        try:
            await self.initialize()

            # Initialize Gemini
            llm = ChatGoogleGenerativeAI(
                google_api_key=GOOGLE_API_KEY,
                model="gemini-2.0-flash-exp",
                temperature=0
            )

            # Create task for GitHub upload
            task = f"""
            Follow these steps precisely:
            1. Go to github.com
            2. Click "Sign in" button
            3. Enter username: {GITHUB_USERNAME}
            4. Enter password: {GITHUB_PASSWORD}
            5. Click the "Repositories" button in top left
            6. Select repository "your_repository_name"
            7. Click "Add file" button
            8. Click "Upload files" option
            9. Use the 'Upload pdf to element' action to upload the file. Try indices 0, 1, and 2.
            10. Add commit message: "Upload PDF file"
            11. Click "Commit changes" button
            """

            # Create and run agent
            agent = Agent(
                task=task,
                llm=llm,
                browser=self.browser,
                browser_context=self.context,
                controller=controller  # Pass the controller instance
            )

            logger.info("Starting PDF upload to GitHub")
            await agent.run()
            logger.info("PDF upload completed successfully")

        except Exception as e:
            logger.error(f"Error during PDF upload: {str(e)}")
            raise
        finally:
            await self.cleanup()

async def main():
    """Main execution function"""
    try:
        # Verify PDF file exists
        if not Path(PDF_PATH).exists():
            raise FileNotFoundError(f"PDF file not found at: {PDF_PATH}")

        automation = BrowserAutomation()
        await automation.upload_pdf_to_github()
        print("✅ PDF upload to GitHub completed successfully")

    except FileNotFoundError as e:
        print(f"❌ Error: {str(e)}")
    except Exception as e:
        print(f"❌ Error during execution: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())