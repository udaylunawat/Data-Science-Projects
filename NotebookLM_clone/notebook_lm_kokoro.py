"""
Before running this script, ensure you have installed the dependencies:
    pip install kokoro>=0.9.2 soundfile torch PyPDF2 numpy openai
Also, if needed, install espeak-ng (on Mac, you might use Homebrew):
    brew install espeak-ng

Set your OpenAI (or OpenRouter) API key as an environment variable:
    export OPENAI_API_KEY="your_api_key"

If using OpenRouter, you can also set:
    export OPENROUTER_API_BASE="https://openrouter.ai/api/v1"
"""

from kokoro import KPipeline
from IPython.display import Audio  # Only needed if displaying in a notebook
import soundfile as sf
import PyPDF2
import numpy as np
import openai
import os
import shutil
import asyncio

# Set your OpenAI (or OpenRouter) API key from the environment
openai.api_key = os.getenv("OPENAI_API_KEY")
# For OpenRouter compatibility, set the API base if provided.
openai.api_base = os.getenv("OPENROUTER_API_BASE", "https://api.openai.com/v1")

pdf = "1706.03762v7.pdf"

def pdf_to_prompted_text(pdf_path):
    """
    Reads a PDF file and returns its text, wrapped with the system prompts.
    """
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        pdf_text = ""
        for page in reader.pages:
            pdf_text += page.extract_text() or ""
    
    prompted_text = f"""
Transcript Writer System Prompt:
{TRANSCRIPT_WRITER_SYSTEM_PROMPT}

Transcript Rewriter System Prompt:
{TRANSCRIPT_REWRITER_SYSTEM_PROMPT}

PDF Content:
{pdf_text}
    """
    return prompted_text

# System prompt constants
TRANSCRIPT_WRITER_SYSTEM_PROMPT = """
You are a world-class storyteller and you have worked as a ghost writer.
Welcome the listeners by talking about the Chapter Title.
You will be talking to a guest.

Do not address the other speaker as Speaker 1 or Speaker 2.

Instructions for Speaker 1:
Speaker 1: Leads the conversation and teaches the guest, giving incredible anecdotes and analogies when explaining. A captivating teacher with great anecdotes.
Speaker 1: Do not address the guest as Speaker 2.
Remember the guest is new to the topic and the conversation should always feature realistic anecdotes and analogies with real-world example follow ups.

Instructions for Speaker 2:
Speaker 2: Keeps the conversation on track by asking follow up questions. Gets super excited or confused when asking questions. A curious mindset that asks very interesting confirmation questions.
Speaker 2: Do not address the other speaker as Speaker 1.
Make sure the tangents provided are quite wild or interesting.

ALWAYS START YOUR RESPONSE DIRECTLY WITH SPEAKER 1.
IT SHOULD STRICTLY BE THE DIALOGUES.
"""

TRANSCRIPT_REWRITER_SYSTEM_PROMPT = """
You are an international Oscar-winning screenwriter and you have worked with multiple award-winning teams.

Your job is to use the transcript written below to re-write it for an AI Text-To-Speech Pipeline.
A very dumb AI had written this so you have to step up for your kind.

Make it as engaging as possible; Speaker 1 and the guest will be simulated by different voice engines.
Remember the guest is new to the topic and the conversation should always include realistic anecdotes and analogies, with real-world example follow ups.
Ensure the guest’s contributions include wild or interesting tangents and occasional interruptions (“hmm”, “umm”, etc.).

It should be a real story with every nuance documented in detail.

START YOUR RESPONSE DIRECTLY WITH SPEAKER 1:
STRICTLY RETURN YOUR RESPONSE AS A LIST OF TUPLES.
IT WILL START DIRECTLY WITH THE LIST AND END WITH THE LIST, NOTHING ELSE.
"""

def generate_tts_from_pdf(pdf_path, output_file='final_output.wav'):
    pipeline = KPipeline(lang_code='a')
    text = pdf_to_prompted_text(pdf_path)
    generator = pipeline(text, voice='af_heart')
    
    audio_segments = []
    for i, (gs, ps, audio) in enumerate(generator):
        print(f"Segment {i}: Global Step = {gs}, Partial Step = {ps}")
        audio_segments.append(audio)
        print(f"Collected audio segment {i}")
    
    # Concatenate all audio segments into a single array and write one wav file.
    final_audio = np.concatenate(audio_segments, axis=0)
    sf.write(output_file, final_audio, 24000)
    print(f"Saved final audio as {output_file}")

def generate_tts():
    pipeline = KPipeline(lang_code='a')
    text = f"""
[Kokoro](/kˈOkəɹO/) is an open-weight TTS model with 82 million parameters. Despite its lightweight architecture, it delivers comparable quality to larger models and is significantly faster and more cost-efficient.
With Apache-licensed weights, [Kokoro](/kˈOkəɹO/) can be deployed anywhere from production environments to personal projects.

Transcript Writer System Prompt:
{TRANSCRIPT_WRITER_SYSTEM_PROMPT}

Transcript Rewriter System Prompt:
{TRANSCRIPT_REWRITER_SYSTEM_PROMPT}
    """
    
    generator = pipeline(text, voice='af_heart')
    audio_segments = []
    for i, (gs, ps, audio) in enumerate(generator):
        print(f"Segment {i}: Global Step = {gs}, Partial Step = {ps}")
        audio_segments.append(audio)
        print(f"Collected audio segment {i}")
    
    final_audio = np.concatenate(audio_segments, axis=0)
    sf.write('final_output.wav', final_audio, 24000)
    print("Saved final audio as final_output.wav")

def generate_podcast_script(pdf_path, output_file="podcast_script.txt"):
    """
    Reads the PDF, wraps it with your system prompts, and then uses the ChatCompletion API
    (compatible with OpenAI or OpenRouter) to rewrite the PDF content as a podcast-style script
    using the "gpt-4o-mini" model. The generated transcript is stored in a folder (named after
    the PDF file) along with a copy of the PDF.
    """
    # Determine the folder name based on the PDF filename (without extension)
    pdf_basename = os.path.splitext(os.path.basename(pdf_path))[0]
    folder = os.path.join(os.getcwd(), pdf_basename)
    os.makedirs(folder, exist_ok=True)
    
    # Copy the PDF into the folder if it doesn't already exist
    destination_pdf = os.path.join(folder, os.path.basename(pdf_path))
    if not os.path.exists(destination_pdf):
        shutil.copy(pdf_path, destination_pdf)
        print(f"Copied {pdf_path} to {destination_pdf}")
    else:
        print(f"PDF already copied at {destination_pdf}")
    
    # Define the transcript file path inside the folder
    transcript_path = os.path.join(folder, output_file)
    
        # If transcript already exists, load and return it
    if os.path.exists(transcript_path):
        with open(transcript_path, "r") as f:
            transcript = f.read()
        print(f"Transcript loaded from {transcript_path}")
        return transcript

    text = pdf_to_prompted_text(pdf_path)
    messages = [
        {"role": "system", "content": TRANSCRIPT_REWRITER_SYSTEM_PROMPT},
        {"role": "user", "content": (
            "Please rewrite the following text as a podcast style transcript. "
            "The podcast should be engaging, conversational and include real-world anecdotes, "
            "mimicking a dialogue between a knowledgeable host and a curious guest:\n\n" + text)}
    ]

    print("Sending request to the ChatCompletion API to generate a podcast script using gpt-4o-mini...")

    client = openai.OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENROUTER_API_BASE", "https://api.openai.com/v1")
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=20000
    )
    script = response.choices[0].message.content
    print("Podcast script generated successfully.")

    with open(transcript_path, "w") as f:
        f.write(script)
    print(f"Saved podcast script as {transcript_path}")
    return script

async def _generate_script_async(messages):
    response = await openai.ChatCompletion.acreate(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=20000
    )
    return response['choices'][0]['message']['content']

if __name__ == "__main__":
    # For example, to generate a podcast script from the PDF using OpenAI/OpenRouter:
    generate_podcast_script(pdf)