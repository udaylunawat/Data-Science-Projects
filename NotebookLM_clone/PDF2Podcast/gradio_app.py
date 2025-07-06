import os
import tempfile
import gradio as gr
import shutil
import ast
import numpy as np
import soundfile as sf
import warnings

try:
    from moshi.models.tts import TTSModel
except ImportError:
    print("Moshi TTSModel not available — install Kyutai’s version via pip.")
    TTSModel = None

from notebook_lm_kokoro import (
    generate_podcast_script,
    generate_audio_from_script,
    generate_audio_kyutai,
    KPipeline,
)

warnings.filterwarnings("ignore")

def process_segment(entry, voice_map):
    speaker, dialogue = entry
    chosen_voice = voice_map.get(speaker, "af_heart")
    pipeline = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M")
    generator = pipeline(dialogue, voice=chosen_voice)
    return np.concatenate([audio for _, _, audio in generator], axis=0) if generator else None

def generate_audio_from_script_with_voices(script, speaker1_voice, speaker2_voice, output_file):
    print("[DEBUG] Raw transcript string:")
    print(script)

    voice_map = {"Speaker 1": speaker1_voice, "Speaker 2": speaker2_voice}
    try:
        transcript_list = ast.literal_eval(script)
        if not isinstance(transcript_list, list):
            raise ValueError("Transcript is not a list")

        entries = [entry for entry in transcript_list if isinstance(entry, tuple) and len(entry) == 2]
        results = [process_segment(entry, voice_map) for entry in entries if entry is not None]

        if not results:
            return None
        sample_rate = 24000
        pause = np.zeros(sample_rate, dtype=np.float32)
        final_audio = results[0]
        for seg in results[1:]:
            final_audio = np.concatenate((final_audio, pause, seg), axis=0)
        sf.write(output_file, final_audio, sample_rate)
        return output_file
    except Exception as e:
        print(f"Transcript parse error: {e}")
        return None

def process_pdf(pdf_file, speaker1_voice, speaker2_voice, kyutai_voice1, kyutai_voice2,
                provider, openai_key=None, openrouter_key=None, openrouter_base=None, tts_engine=None):
    try:
        if provider == "openai" and not openai_key:
            return "OpenAI API key is required", None
        if provider == "openrouter" and not openrouter_key:
            return "OpenRouter API key is required", None

        if provider in ["openai", "kyutai"]:
            os.environ["OPENAI_API_KEY"] = openai_key or ""
            os.environ["OPENROUTER_API_BASE"] = "https://api.openai.com/v1"
        if provider in ["openrouter", "kyutai"]:
            os.environ["OPENAI_API_KEY"] = openrouter_key or ""
            os.environ["OPENROUTER_API_BASE"] = openrouter_base or "https://openrouter.ai/api/v1"

        if pdf_file is None:
            return "No file uploaded", None

        tmp_path = pdf_file.name

        script_provider = "openrouter" if provider == "kyutai" and openrouter_key else provider
        transcript, _ = generate_podcast_script(pdf_file.name, provider=script_provider)

        if transcript is None:
            return "Transcript generation failed: got None", None
        if not transcript.strip().startswith("["):
            return f"Malformed transcript:\n{transcript}", None

        audio_path = os.path.join(os.path.dirname(tmp_path), f"audio_{os.path.basename(tmp_path).replace('.pdf', '.wav')}")

        if tts_engine == "kyutai":
            result = generate_audio_kyutai(transcript, kyutai_voice1, kyutai_voice2, audio_path)
        else:
            result = generate_audio_from_script_with_voices(transcript, speaker1_voice, speaker2_voice, audio_path)

        return ("Process complete!", result) if result else ("Error generating audio", None)
    except Exception as e:
        print(f"process_pdf error: {e}")
        return f"Error: {e}", None

def update_ui(provider, tts_engine):
    return [
        gr.update(visible=tts_engine == "kokoro"),
        gr.update(visible=tts_engine == "kokoro"),
        gr.update(visible=tts_engine == "kyutai"),
        gr.update(visible=tts_engine == "kyutai"),
        gr.update(visible=provider in ["openai", "kyutai"]),
        gr.update(visible=provider in ["openrouter", "kyutai"]),
        gr.update(visible=provider == "openrouter"),
    ]

def create_gradio_app():
    css = ".gradio-container {max-width: 900px !important}"
    with gr.Blocks(css=css, theme=gr.themes.Soft()) as app:
        gr.Markdown("# 🎧 PDF to Podcast — NotebookLM + Kokoro/Kyutai")

        pdf_input = gr.File(file_types=[".pdf"], type="filepath", label="📄 Upload your PDF", scale=2)

        with gr.Row():
            speaker1_voice = gr.Dropdown(["af_heart", "af_bella", "hf_beta"], value="af_heart", label="Speaker 1 Voice")
            speaker2_voice = gr.Dropdown(["af_nicole", "af_heart", "bf_emma"], value="bf_emma", label="Speaker 2 Voice")
            provider = gr.Radio(["openai", "openrouter"], value="openrouter", label="API Provider")
            openai_key = gr.Textbox(type="password", label="OpenAI Key")
            openrouter_key = gr.Textbox(type="password", label="OpenRouter Key")
            openrouter_base = gr.Textbox(placeholder="https://openrouter.ai/api/v1", label="OpenRouter Base URL")
            tts_engine = gr.Radio(["kokoro", "kyutai"], value="kokoro", label="TTS Engine")

        with gr.Row():
            kyutai_voice1 = gr.Dropdown([
                "expresso/ex03-ex01_happy_001_channel1_334s.wav",
                "expresso/ex03-ex02_narration_001_channel1_674s.wav",
                "vctk/p226_023_mic1.wav"
            ],
            value="expresso/ex03-ex01_happy_001_channel1_334s.wav",
            label="Kyutai Voice 1",
            visible=True)

            kyutai_voice2 = gr.Dropdown([
                "expresso/ex03-ex01_happy_001_channel1_334s.wav",
                "expresso/ex03-ex02_narration_001_channel1_674s.wav",
                "vctk/p225_023_mic1.wav"
            ],
            value="expresso/ex03-ex02_narration_001_channel1_674s.wav",
            label="Kyutai Voice 2",
            visible=True)

        submit_btn = gr.Button("🎙️ Generate Podcast", variant="primary")
        status_output = gr.Textbox(label="📝 Status", interactive=False)
        audio_output = gr.Audio(type="filepath", label="🎵 Your Podcast")

        submit_btn.click(
            process_pdf,
            inputs=[pdf_input, speaker1_voice, speaker2_voice, kyutai_voice1, kyutai_voice2,
                    provider, openai_key, openrouter_key, openrouter_base, tts_engine],
            outputs=[status_output, audio_output]
        )

        provider.change(update_ui, [provider, tts_engine],
                        [speaker1_voice, speaker2_voice, kyutai_voice1, kyutai_voice2,
                         openai_key, openrouter_key, openrouter_base])
        tts_engine.change(update_ui, [provider, tts_engine],
                          [speaker1_voice, speaker2_voice, kyutai_voice1, kyutai_voice2,
                           openai_key, openrouter_key, openrouter_base])

        gr.Markdown("""
        **📌 Tips**
        - Upload a clean, structured PDF.
        - Pick your API provider and enter relevant keys.
        - Choose the TTS engine and customize voices.
        """)

    return app

if __name__ == "__main__":
    create_gradio_app().queue().launch(server_name="0.0.0.0", server_port=7860, share=True, debug=True, pwa=True)
