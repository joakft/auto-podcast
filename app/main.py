"""
Gradio app:
- Select prompt style (Portuguese kids story, English study podcast, Spanish fable)
- Left: user idea + length slider
- Right: generated narrative
- Audio: generate, play inline, delete
"""

import os
import gradio as gr
import openai
from dotenv import load_dotenv
from pathlib import Path
from app.prompts import PROMPTS
from app.storage import upload_file
from app.rss_utils import add_episode
from datetime import datetime

client = openai.OpenAI()


# Load API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Ensure tmp folder exists
TMP_DIR = Path("tmp")
TMP_DIR.mkdir(exist_ok=True)

last_text = ""
filename = f"episode_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.mp3"
last_audio_file = TMP_DIR / filename

def upload_to_podcast(title: str):
    """Upload last audio and update RSS feed on S3."""
    global last_audio_file, last_text
    if not last_audio_file.exists():
        return "Nenhum áudio disponível para upload."

    # Upload MP3 to S3
    s3_key = f"episodes/{last_audio_file.name}"
    audio_url = upload_file(last_audio_file, s3_key)

    # Update local RSS feed
    status = add_episode(
        title=title or "AI Generated Narrative",
        description=last_text,
        audio_url=audio_url
    )

    # Upload RSS feed too
    rss_url = upload_file(Path("feed.xml"), "rss/feed.xml")

    return f"{status}\nRSS feed uploaded: {rss_url}"

def generate_narrative(user_prompt: str, length: int, style: str) -> str:
    """Generate narrative based on user input, length, and selected style."""
    global last_text

    if not user_prompt.strip():
        return "(Please type something...)"

    system_prompt = PROMPTS.get(style, "You are a helpful assistant.")

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Write a narrative of about {length} words based on this idea:\n{user_prompt}"
            },
        ],
    )
    last_text = response.choices[0].message.content
    return last_text


def make_audio():
    """Generate audio of the last narrative."""
    global last_text, last_audio_file

    if not last_text:
        return None, "No text available to convert."

    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="nova",
        input=(
            f"{last_text}"
        ),
        instructions=("Please read the following text in a deep, authoritative voice. "
            "Speak with a lot of inflexion to persuade, pausing for a beat after each sentence."
        ),
        speed = 0.85
            
    )
    response.stream_to_file(last_audio_file)

    return str(last_audio_file), f"Audio saved to {last_audio_file}"


def delete_audio():
    """Delete last audio file if it exists."""
    global last_audio_file
    if last_audio_file.exists():
        last_audio_file.unlink()
        return None, "Audio deleted."
    return None, "No audio file to delete."


# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("## 🌍 Multilingual Narrative Generator")

    with gr.Row():
        with gr.Column(scale=1):
            style_dropdown = gr.Dropdown(
                choices=list(PROMPTS.keys()),
                value=list(PROMPTS.keys())[0],
                label="Choose narrative style"
            )
            prompt_box = gr.Textbox(
                label="Your idea / topic",
                placeholder="Type your idea here..."
            )
            length_slider = gr.Slider(
                minimum=100, maximum=1000, step=50, value=300,
                label="Length of narrative (words)"
            )
        with gr.Column(scale=2):
            output_box = gr.Textbox(
                label="Generated Narrative",
                interactive=False,
                lines=20
            )

    with gr.Row():
        gen_audio = gr.Button("🔊 Generate Audio")
        del_audio = gr.Button("🗑️ Delete Audio")

    with gr.Row():
        audio_player = gr.Audio(
            label="Listen to audio",
            interactive=False,
            type="filepath"
        )
        audio_status = gr.Textbox(
            label="Audio status",
            interactive=False
        )

    with gr.Row():
        upload_title = gr.Textbox(label="Episode title", placeholder="Enter episode title...")
        upload_button = gr.Button("📤 Upload to Podcast (RSS)")
        upload_status = gr.Textbox(label="RSS status", interactive=False)
        
    upload_button.click(
        fn=upload_to_podcast,
        inputs=upload_title,
        outputs=upload_status
    )

    # Narrative generation
    prompt_box.submit(
        fn=generate_narrative,
        inputs=[prompt_box, length_slider, style_dropdown],
        outputs=output_box
    )
    length_slider.change(
        fn=generate_narrative,
        inputs=[prompt_box, length_slider, style_dropdown],
        outputs=output_box
    )
    style_dropdown.change(
        fn=generate_narrative,
        inputs=[prompt_box, length_slider, style_dropdown],
        outputs=output_box
    )

    # Audio actions
    gen_audio.click(
        fn=make_audio,
        inputs=None,
        outputs=[audio_player, audio_status]
    )
    del_audio.click(
        fn=delete_audio,
        inputs=None,
        outputs=[audio_player, audio_status]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
