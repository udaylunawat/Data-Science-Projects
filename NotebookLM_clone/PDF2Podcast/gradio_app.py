import os
import tempfile
import gradio as gr
import shutil
import ast
import numpy as np
import soundfile as sf
import warnings
import multiprocessing
import concurrent.futures

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
NUM_WORKERS = multiprocessing.cpu_count()

def process_segment(entry_and_voice_map):
    entry, voice_map = entry_and_voice_map
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

        entries = [(entry, voice_map) for entry in transcript_list if isinstance(entry, tuple) and len(entry) == 2]
        with concurrent.futures.ProcessPoolExecutor(max_workers=NUM_WORKERS) as executor:
            results = [r for r in executor.map(process_segment, entries) if r is not None]
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

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            shutil.copy2(pdf_file.name, tmp.name)
            tmp_path = tmp.name

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
            with concurrent.futures.ProcessPoolExecutor(max_workers=NUM_WORKERS) as executor:
                result = executor.submit(
                    generate_audio_from_script_with_voices,
                    transcript, speaker1_voice, speaker2_voice, audio_path
                ).result()

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

        with gr.Row():
            with gr.Column(scale=1.5):
                pdf_input = gr.File(file_types=[".pdf"], type="filepath", label="📄 Upload your PDF")
                provider = gr.Radio(["openai", "openrouter"], value="openrouter", label="🧠 API Provider")
                tts_engine = gr.Radio(["kokoro", "kyutai"], value="kokoro", label="🎤 TTS Engine")

                speaker1_voice = gr.Dropdown(["af_heart","af_bella","hf_beta"], value="af_heart", label="Speaker 1 Voice", visible=True)
                speaker2_voice = gr.Dropdown(["af_nicole","af_heart","bf_emma"], value="bf_emma", label="Speaker 2 Voice", visible=True)
                kyutai_voice1 = gr.Dropdown(
                    [
                        "expresso/ex03-ex01_happy_001_channel1_334s.wav",
                        "expresso/ex03-ex02_narration_001_channel1_674s.wav",
                        "vctk/p226_023_mic1.wav"
                    ],
                    value="expresso/ex03-ex01_happy_001_channel1_334s.wav",
                    label="Kyutai Voice 1",
                    visible=True
                )

                kyutai_voice2 = gr.Dropdown(
                    [
                        "expresso/ex03-ex01_happy_001_channel1_334s.wav",
                        "expresso/ex03-ex02_narration_001_channel1_674s.wav",
                        "vctk/p225_023_mic1.wav"
                    ],
                    value="expresso/ex03-ex02_narration_001_channel1_674s.wav",
                    label="Kyutai Voice 2",
                    visible=True
                )

                with gr.Accordion("🔐 API Keys", open=True):
                    openai_key = gr.Textbox(type="password", label="OpenAI Key", show_label=True, visible=True)
                    openrouter_key = gr.Textbox(type="password", label="OpenRouter Key", show_label=True, visible=True)
                    openrouter_base = gr.Textbox(placeholder="https://openrouter.ai/api/v1", label="OpenRouter Base URL", visible=True)

                submit_btn = gr.Button("🎙️ Generate Podcast", variant="primary")

            with gr.Column(scale=1):
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
        - Pick your API provider and then set appropriate keys.
        - Choose **TTS Engine** (Kokoro/Kyutai) to reveal relevant voice options.
        - Works well with clean, structured PDFs.
        """)

    return app

if __name__ == "__main__":
    create_gradio_app().queue().launch(server_name="0.0.0.0", server_port=7860, share=True, debug=True, pwa=True)