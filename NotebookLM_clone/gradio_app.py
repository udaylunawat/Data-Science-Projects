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
warnings.filterwarnings("ignore")

# A modified version of generate_audio_from_script to accept voice mapping
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
        # Process each dialogue entry
        for i, entry in enumerate(transcript_list):
            if not isinstance(entry, tuple) or len(entry) != 2:
                print(f"Skipping invalid entry {i}: {entry}")
                continue

            speaker, dialogue = entry
            chosen_voice = voice_map.get(speaker, "af_heart")
            print(f"Generating audio for {speaker} with voice '{chosen_voice}'...")

            pipeline = KPipeline(lang_code="a")
            generator = pipeline(dialogue, voice=chosen_voice)

            segment_audio = []
            for j, (gs, ps, audio) in enumerate(generator):
                # print(f"{speaker} - Segment {j}: Global Step = {gs}, Partial Step = {ps}")
                segment_audio.append(audio)

            if segment_audio:
                segment_full = np.concatenate(segment_audio, axis=0)
                all_audio_segments.append(segment_full)

        if not all_audio_segments:
            print("No audio segments were generated.")
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


def process_pdf(pdf_file, speaker1_voice, speaker2_voice, provider):
    """Process the uploaded PDF file and generate audio"""
    try:
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
        
        result = generate_audio_from_script_with_voices(
            transcript, 
            speaker1_voice, 
            speaker2_voice, 
            output_file=audio_output_path
        )
        
        if result is None:
            return "Error generating audio", None
        
        return "Process complete!", result

    except Exception as e:
        print(f"Error in process_pdf: {str(e)}")
        return f"Error processing file: {str(e)}", None


def create_gradio_app():
    with gr.Blocks() as app:
        gr.Markdown("# NotebookLM-Kokoro TTS App")
        gr.Markdown("Upload a PDF, choose voices, and generate TTS audio using Kokoro.")
        
        with gr.Row():
            pdf_input = gr.File(label="Upload PDF", file_types=[".pdf"])
        
        with gr.Row():
            with gr.Column():
                speaker1_voice = gr.Dropdown(
                    choices=["af_heart", "af_bella", "hf_beta"],
                    value="af_heart",
                    label="Speaker 1 Voice"
                )
                speaker2_voice = gr.Dropdown(
                    choices=["af_nicole", "af_heart", "bf_emma"],
                    value="af_nicole",
                    label="Speaker 2 Voice"
                )
                provider = gr.Radio(
                    choices=["openai", "openrouter"],
                    value="openrouter",
                    label="API Provider (TTS Script Generation)"
                )
                submit_btn = gr.Button("Generate Audio")
        
        with gr.Row():
            status_output = gr.Textbox(label="Status")
            audio_output = gr.Audio(label="Generated Audio", type="filepath")
        
        submit_btn.click(
            fn=process_pdf,
            inputs=[pdf_input, speaker1_voice, speaker2_voice, provider],
            outputs=[status_output, audio_output]
        )
    
    return app


if __name__ == "__main__":
    demo = create_gradio_app()
    demo.launch(share=True)  # add share=True to get a public URL