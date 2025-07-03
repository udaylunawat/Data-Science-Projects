# filepath: /Users/udaylunawat/Downloads/Data-Science-Projects/NotebookLM_clone/gradio_app.py
import os
import tempfile
import gradio as gr
from notebook_lm_kokoro import generate_podcast_script, KPipeline
import soundfile as sf
import numpy as np
import ast
import shutil
import warnings
import os
import gradio as gr
import concurrent.futures
import multiprocessing
from notebook_lm_kokoro import generate_podcast_script, generate_audio_from_script
warnings.filterwarnings("ignore")

# Define number of workers based on CPU cores
NUM_WORKERS = multiprocessing.cpu_count()  # Gets total CPU cores

def process_segment(entry_and_voice_map):
    entry, voice_map = entry_and_voice_map  # Unpack the tuple
    speaker, dialogue = entry
    chosen_voice = voice_map.get(speaker, "af_heart")
    print(f"Generating audio for {speaker} with voice '{chosen_voice}'...")
    
    pipeline = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M")
    generator = pipeline(dialogue, voice=chosen_voice)
    
    segment_audio = []
    for _, _, audio in generator:
        segment_audio.append(audio)
        
    if segment_audio:
        return np.concatenate(segment_audio, axis=0)
    return None

def generate_audio_from_script_with_voices(script, speaker1_voice, speaker2_voice, output_file):
    voice_map = {"Speaker 1": speaker1_voice, "Speaker 2": speaker2_voice}
    
    # Clean up the script string if needed
    script = script.strip()
    if not script.startswith("[") or not script.endswith("]"):
        print("Invalid transcript format. Expected a list of tuples.")
        return None

    try:
        transcript_list = ast.literal_eval(script)
        if not isinstance(transcript_list, list):
            raise ValueError("Transcript is not a list")

        all_audio_segments = []
        # Prepare input data with voice_map for each entry
        entries_with_voice_map = [(entry, voice_map) for entry in transcript_list]

        try:
            # Process segments in parallel
            with concurrent.futures.ProcessPoolExecutor(max_workers=NUM_WORKERS) as executor:
                # Map the processing function across all dialogue entries
                results = list(executor.map(process_segment, entries_with_voice_map))
                
                # Filter out None results and combine audio segments
                all_audio_segments = [r for r in results if r is not None]
        
        except Exception as e:
            print(f"Error during audio generation: {e}")
            return None
        
        if not all_audio_segments:
            print("No audio segments were generated")
            return None

        # Add a pause between segments
        sample_rate = 24000
        pause = np.zeros(sample_rate, dtype=np.float32)
        final_audio = all_audio_segments[0]
        for seg in all_audio_segments[1:]:
            final_audio = np.concatenate((final_audio, pause, seg), axis=0)

        sf.write(output_file, final_audio, sample_rate)
        print(f"Saved final audio as {output_file}")
        return output_file

    except Exception as e:
        print(f"Error processing transcript: {e}")
        return None


def process_pdf(pdf_file, speaker1_voice, speaker2_voice, provider, api_key, openrouter_base=None):
    """Process the uploaded PDF file and generate audio"""
    try:
    
        # Set API configuration based on provider
        if provider == "openai":
            os.environ["OPENAI_API_KEY"] = api_key
            os.environ["OPENROUTER_API_BASE"] = "https://api.openai.com/v1"
        else:
            os.environ["OPENAI_API_KEY"] = api_key
            os.environ["OPENROUTER_API_BASE"] = openrouter_base or "https://openrouter.ai/api/v1"
        # Check if we received a valid file
        if pdf_file is None:
            return "No file uploaded", None
            
        # Create a temporary file with .pdf extension
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            # For Gradio uploads, we need to copy the file
            shutil.copy2(pdf_file.name, tmp.name)
            tmp_path = tmp.name
            
        print(f"Uploaded PDF saved at {tmp_path}")

        # Generate transcript using your existing function
        transcript, transcript_path = generate_podcast_script(tmp_path, provider=provider)
        if transcript is None:
            return "Error generating transcript", None

        # Define an output file path for the generated audio
        audio_output_path = os.path.join(
            os.path.dirname(tmp_path),
            f"audio_{os.path.basename(tmp_path).replace('.pdf', '.wav')}"
        )
        
        # result = generate_audio_from_script_with_voices(
        #     transcript, 
        #     speaker1_voice, 
        #     speaker2_voice, 
        #     output_file=audio_output_path
        # )

        # Use ProcessPoolExecutor with explicit number of workers
        with concurrent.futures.ProcessPoolExecutor(max_workers=NUM_WORKERS) as executor:
            print(f"Processing with {NUM_WORKERS} CPU cores")
            # Submit audio generation task to the executor
            future = executor.submit(
                generate_audio_from_script_with_voices,
                transcript, speaker1_voice, speaker2_voice, audio_output_path
            )
            result = future.result()
            
            if result is None:
                return "Error generating audio", None
            
            return "Process complete!", result

    except Exception as e:
        print(f"Error in process_pdf: {str(e)}")
        return f"Error processing file: {str(e)}", None
        
        if result is None:
            return "Error generating audio", None
        
        return "Process complete!", result

    except Exception as e:
        print(f"Error in process_pdf: {str(e)}")
        return f"Error processing file: {str(e)}", None


def create_gradio_app():
    # Add CSS for better styling
    css = """
    .gradio-container {max-width: 900px !important}
    """
    
    with gr.Blocks(css=css, theme=gr.themes.Soft()) as app:
        gr.Markdown(
            """
            # 📚 NotebookLM-Kokoro TTS App
            Upload a PDF, choose voices, and generate conversational audio using Kokoro TTS.
            """
        )
        
        with gr.Row():
            with gr.Column(scale=2):
                pdf_input = gr.File(
                    label="Upload PDF Document",
                    file_types=[".pdf"],
                    type="filepath"
                )
                
                with gr.Row():
                    speaker1_voice = gr.Dropdown(
                        choices=["af_heart", "af_bella", "hf_beta"],
                        value="af_heart",
                        label="Speaker 1 Voice"
                    )
                    speaker2_voice = gr.Dropdown(
                        choices=["af_nicole", "af_heart", "bf_emma"],
                        value="bf_emma",
                        label="Speaker 2 Voice"
                    )
                

                with gr.Group():
                    provider = gr.Radio(
                        choices=["openai", "openrouter"],
                        value="openrouter",
                        label="API Provider"
                    )
                    
                    api_key = gr.Textbox(
                        label="API Key",
                        placeholder="Enter your API key here...",
                        type="password",
                        elem_classes="api-input"
                    )
                    
                    openrouter_base = gr.Textbox(
                        label="OpenRouter Base URL (optional)",
                        placeholder="https://openrouter.ai/api/v1",
                        visible=False,
                        elem_classes="api-input"
                    )

                    # Show/hide OpenRouter base URL based on provider selection
                    def toggle_openrouter_base(provider_choice):
                        return gr.update(visible=provider_choice == "openrouter")
                    
                    provider.change(
                        fn=toggle_openrouter_base,
                        inputs=[provider],
                        outputs=[openrouter_base]
                    )
                
                submit_btn = gr.Button("🎙️ Generate Audio", variant="primary")
            
            with gr.Column(scale=2):
                status_output = gr.Textbox(
                    label="Status",
                    placeholder="Processing status will appear here..."
                )
                audio_output = gr.Audio(
                    label="Generated Audio",
                    type="filepath"
                )
        
        # # Examples section
        # gr.Examples(
        #     examples=[
        #         ["sample.pdf", "af_heart", "af_nicole", "openrouter", "your-api-key-here", "https://openrouter.ai/api/v1"],
        #     ],
        #     inputs=[pdf_input, speaker1_voice, speaker2_voice, provider, api_key, openrouter_base],
        #     outputs=[status_output, audio_output],
        #     fn=process_pdf,
        #     cache_examples=True,
        # )
        
        submit_btn.click(
            fn=process_pdf,
            inputs=[
                pdf_input, 
                speaker1_voice, 
                speaker2_voice, 
                provider,
                api_key,
                openrouter_base
            ],
            outputs=[status_output, audio_output],
            api_name="generate"
        )
        
        gr.Markdown(
            """
            ### 📝 Notes
            - Make sure your PDF is readable and contains text (not scanned images)
            - Processing large PDFs may take a few minutes
            - You need a valid OpenAI/OpenRouter API key set as environment variable
            """
        )
    
    return app

if __name__ == "__main__":
    demo = create_gradio_app()
    demo.queue().launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        debug=True,
        pwa=True
    )