import os
import asyncio
import gradio as gr
from dotenv import load_dotenv, set_key, find_dotenv
import tempfile
from pathlib import Path

class GradioInterface:
    def __init__(self, llm_manager, browser_automation):
        self.llm_manager = llm_manager
        self.automation = browser_automation
        self.dotenv_path = find_dotenv()
        self.temp_dir = Path(tempfile.mkdtemp())

    def get_model_choices(self):
        return [f"{id}. {model['name']} ({model['provider']})"
                for id, model in self.llm_manager.MODELS.items()]

    def check_api_key(self, model_id):
        model_id = model_id.split('.')[0]
        if model_id in self.llm_manager.MODELS:
            key_env = self.llm_manager.MODELS[model_id]["key_env"]
            return bool(os.getenv(key_env))
        return False

    def update_api_key(self, model_choice, api_key):
        try:
            model_id = model_choice.split('.')[0]
            if model_id in self.llm_manager.MODELS:
                model = self.llm_manager.MODELS[model_id]
                set_key(self.dotenv_path, model["key_env"], api_key)
                load_dotenv(self.dotenv_path)
                return f"API key for {model['name']} updated successfully"
            return "Invalid model selection"
        except Exception as e:
            return f"Error updating API key: {str(e)}"

    async def run_task_async(self, model_choice, task):
        try:
            model_id = model_choice.split('.')[0]
            if not model_id in self.llm_manager.MODELS:
                return "Invalid model selection", "", None

            if not self.check_api_key(model_id):
                return f"No API key set for {self.llm_manager.MODELS[model_id]['name']}", "", None

            if not task.strip():
                return "Task cannot be empty", "", None

            message_queue = asyncio.Queue()
            screenshot_queue = asyncio.Queue()

            await self.automation.run_task(
                task,
                model_id,
                message_queue=message_queue,
                screenshot_queue=screenshot_queue
            )

            messages = []
            while not message_queue.empty():
                messages.append(await message_queue.get())

            # Check for agent_history.gif in the project directory
            gif_path = os.path.join(os.getcwd(), "agent_history.gif")
            if os.path.exists(gif_path):
                return "Task completed successfully", "\n".join(messages), gif_path
            return "Task completed successfully", "\n".join(messages), None

        except Exception as e:
            return f"Error executing task: {str(e)}", "", None

    def run_task(self, model_choice, task):
        return asyncio.run(self.run_task_async(model_choice, task))

def create_gradio_interface(llm_manager, browser_automation):
    interface = GradioInterface(llm_manager, browser_automation)

    with gr.Blocks(title="Browser Automation System") as demo:
        gr.Markdown("# Browser Automation System")

        with gr.Tab("Run Task"):
            with gr.Row():
                with gr.Column():
                    model_dropdown = gr.Dropdown(
                        choices=interface.get_model_choices(),
                        label="Select Model",
                        info="Choose the LLM model to use"
                    )
                    task_input = gr.Textbox(
                        lines=3,
                        label="Task Description",
                        placeholder="Enter your task here..."
                    )
                    run_button = gr.Button("Run Task")

                with gr.Column():
                    message_output = gr.Textbox(
                        label="Task Progress",
                        lines=10,
                        interactive=False
                    )
                    screenshot_output = gr.Image(
                        label="Task Recording",
                        type="filepath",
                        format="gif"  # Explicitly specify GIF format
                    )
                    output = gr.Textbox(label="Final Status", lines=2)

            run_button.click(
                fn=interface.run_task,
                inputs=[model_dropdown, task_input],
                outputs=[output, message_output, screenshot_output]
            )

        with gr.Tab("API Key Management"):
            api_model_dropdown = gr.Dropdown(
                choices=interface.get_model_choices(),
                label="Select Model",
                info="Choose the model to update API key"
            )
            api_key_input = gr.Textbox(
                label="API Key",
                type="password",
                placeholder="Enter API key here"
            )
            update_button = gr.Button("Update API Key")
            api_status = gr.Textbox(label="Status", lines=1)

            update_button.click(
                fn=interface.update_api_key,
                inputs=[api_model_dropdown, api_key_input],
                outputs=api_status
            )

    return demo