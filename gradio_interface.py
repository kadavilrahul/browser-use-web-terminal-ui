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

    async def run_task(self, model_choice, task, continue_task=False):
        try:
            model_id = model_choice.split('.')[0]
            if not model_id in self.llm_manager.MODELS:
                return "Invalid model selection", "", None, gr.update(visible=False), gr.update(visible=False)

            if not self.llm_manager.check_api_key(model_id):
                return f"No API key set for {self.llm_manager.MODELS[model_id]['name']}", "", None, gr.update(visible=False), gr.update(visible=False)

            if not task.strip():
                return "Task cannot be empty", "", None, gr.update(visible=False), gr.update(visible=False)

            # Create message and screenshot queues
            message_queue = asyncio.Queue()
            screenshot_queue = asyncio.Queue()

            # Run task with queues
            await self.automation.run_task(
                task,
                model_id,
                message_queue=message_queue,
                screenshot_queue=screenshot_queue
            )

            # Get messages and screenshots
            messages = []
            while not message_queue.empty():
                messages.append(await message_queue.get())

            # Check for agent_history.gif in the project directory
            gif_path = os.path.join(os.getcwd(), "agent_history.gif")
            
            # Show continue buttons after task completion
            return ("Task completed successfully. Would you like to perform another task?", 
                    "\n".join(messages), 
                    gif_path if os.path.exists(gif_path) else None,
                    gr.update(visible=True),  # Yes button
                    gr.update(visible=True))  # No button

        except Exception as e:
            return f"Error executing task: {str(e)}", "", None, gr.update(visible=False), gr.update(visible=False)

    async def cleanup_and_exit(self):
        await self.automation.cleanup()
        # Exit the entire process
        os._exit(0)
        return ("Browser closed. Exiting...", 
                "", 
                None,
                gr.update(visible=False),
                gr.update(visible=False))

    def create_interface(self):
        with gr.Blocks() as interface:
            with gr.Row():
                with gr.Column():
                    model_choices = self.get_model_choices()
                    model_dropdown = gr.Dropdown(
                        model_choices,
                        label="Select AI Model",
                        interactive=True
                    )
                    task_input = gr.Textbox(
                        label="Task Description",
                        lines=3,
                        placeholder="Enter your task here...",
                        interactive=True
                    )
                    with gr.Row():
                        run_button = gr.Button("Run Task")
                    with gr.Row():
                        yes_button = gr.Button("Yes, New Task", visible=False)
                        no_button = gr.Button("No, Close Browser", visible=False)

                with gr.Column():
                    output = gr.Textbox(label="Status", lines=2)
                    message_output = gr.Textbox(
                        label="Task Progress",
                        lines=10,
                        interactive=False
                    )
                    screenshot_output = gr.Image(
                        label="Task Recording",
                        type="filepath",
                        format="gif"
                    )

            run_button.click(
                fn=self.run_task,
                inputs=[model_dropdown, task_input],
                outputs=[output, message_output, screenshot_output, yes_button, no_button]
            )

            yes_button.click(
                fn=lambda: ("Enter your next task", "", None, gr.update(visible=False), gr.update(visible=False)),
                outputs=[output, message_output, screenshot_output, yes_button, no_button]
            )

            no_button.click(
                fn=self.cleanup_and_exit,
                outputs=[output, message_output, screenshot_output, yes_button, no_button]
            )

        return interface

def create_gradio_interface(llm_manager, browser_automation):
    interface = GradioInterface(llm_manager, browser_automation)
    return interface.create_interface()