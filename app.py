import gradio as gr
demo = gr.Interface(lambda name: f"Hello {name}!", "text", "text")
demo.launch()
