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
import ast
import json
import warnings
warnings.filterwarnings("ignore")

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
Ensure the guest's contributions include wild or interesting tangents and occasional interruptions ("hmm", "umm", etc.).

It should be a real story with every nuance documented in detail.

IMPORTANT FORMAT INSTRUCTIONS:
You must return a JSON array of arrays, where each inner array contains exactly two strings:
1. The speaker label (either "Speaker 1" or "Speaker 2")
2. The dialogue text

Example format:
[
    ["Speaker 1", "Welcome everyone..."],
    ["Speaker 2", "Thanks for having me..."],
    ["Speaker 1", "Let me explain..."]
]

YOUR RESPONSE MUST BE VALID JSON.
NO OTHER TEXT BEFORE OR AFTER THE JSON ARRAY.
"""


def generate_tts_from_pdf(pdf_path, output_file="final_output.wav"):
    pipeline = KPipeline(lang_code="a")
    text = pdf_to_prompted_text(pdf_path)
    generator = pipeline(text, voice="af_heart")

    audio_segments = []
    for i, (gs, ps, audio) in enumerate(generator):
        print(f"Segment {i}: Global Step = {gs}, Partial Step = {ps}")
        audio_segments.append(audio)
        print(f"Collected audio segment {i}")

    # Concatenate all audio segments into a single array and write one wav file.
    final_audio = np.concatenate(audio_segments, axis=0)
    sf.write(output_file, final_audio, 24000)
    print(f"Saved final audio as {output_file}")


def generate_audio_from_script(script, output_file="podcast_audio.wav"):
    """
    Uses Kokoro TTS to generate audio from the provided transcript.
    Expects a transcript in the format of a list of tuples: [("Speaker 1", "dialogue"), ("Speaker 2", "dialogue"), ...]
    """
    voice_map = {"Speaker 1": "af_heart", "Speaker 2": "af_nicole"}

    # Clean up the script string if needed
    script = script.strip()
    if not script.startswith("[") or not script.endswith("]"):
        print("Invalid transcript format. Expected a list of tuples.")
        return

    try:
        # Parse the transcript
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

            # Updated KPipeline initialization with explicit repo_id
            pipeline = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M")
            generator = pipeline(dialogue, voice=chosen_voice)

            segment_audio = []
            for j, (gs, ps, audio) in enumerate(generator):
                # print(
                #     f"{speaker} - Segment {j}: Global Step = {gs}, Partial Step = {ps}"
                # )
                segment_audio.append(audio)

            if segment_audio:
                segment_full = np.concatenate(segment_audio, axis=0)
                all_audio_segments.append(segment_full)

        if not all_audio_segments:
            print("No audio segments were generated.")
            return

        # Add a pause between segments
        sample_rate = 24000
        pause = np.zeros(sample_rate, dtype=np.float32)
        final_audio = all_audio_segments[0]
        for seg in all_audio_segments[1:]:
            final_audio = np.concatenate((final_audio, pause, seg), axis=0)

        sf.write(output_file, final_audio, sample_rate)
        print(f"Saved final audio as {output_file}")

    except Exception as e:
        print(f"Error processing transcript: {e}")
        return


def generate_tts():
    pipeline = KPipeline(lang_code="a")
    text = f"""
[Kokoro](/kˈOkəɹO/) is an open-weight TTS model with 82 million parameters. Despite its lightweight architecture, it delivers comparable quality to larger models and is significantly faster and more cost-efficient.
With Apache-licensed weights, [Kokoro](/kˈOkəɹO/) can be deployed anywhere from production environments to personal projects.

Transcript Writer System Prompt:
{TRANSCRIPT_WRITER_SYSTEM_PROMPT}

Transcript Rewriter System Prompt:
{TRANSCRIPT_REWRITER_SYSTEM_PROMPT}
    """

    generator = pipeline(text, voice="af_heart")
    audio_segments = []
    for i, (gs, ps, audio) in enumerate(generator):
        print(f"Segment {i}: Global Step = {gs}, Partial Step = {ps}")
        audio_segments.append(audio)
        print(f"Collected audio segment {i}")

    final_audio = np.concatenate(audio_segments, axis=0)
    sf.write("final_output.wav", final_audio, 24000)
    print("Saved final audio as final_output.wav")


def generate_podcast_script(
    pdf_path, output_file="podcast_script.txt", provider="openai"
):
    """
    Reads the PDF, wraps it with your system prompts, and then uses the ChatCompletion API
    (OpenAI or OpenRouter) to rewrite the PDF content as a podcast-style script using "gpt-4o-mini".
    The generated transcript is stored in a folder (named after the PDF file) along with a copy of the PDF.
    Set provider="openrouter" to use OpenRouter, otherwise uses OpenAI.
    """
    pdf_basename = os.path.splitext(os.path.basename(pdf_path))[0]
    folder = os.path.join(os.getcwd(), pdf_basename)
    os.makedirs(folder, exist_ok=True)

    destination_pdf = os.path.join(folder, os.path.basename(pdf_path))
    if not os.path.exists(destination_pdf):
        shutil.copy(pdf_path, destination_pdf)
        print(f"Copied {pdf_path} to {destination_pdf}")
    else:
        print(f"PDF already copied at {destination_pdf}")

    transcript_path = os.path.join(folder, output_file)
    # If transcript exists, load and return it without calling the API.
    if os.path.exists(transcript_path):
        with open(transcript_path, "r") as f:
            transcript = f.read()
        print(f"Transcript loaded from {transcript_path}")
        return transcript, transcript_path

    # Otherwise, generate the transcript.
    text = pdf_to_prompted_text(pdf_path)
    
    messages = [
        {"role": "system", "content": TRANSCRIPT_REWRITER_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "Convert the following text into a dialogue between two speakers.\n\n"
                "REQUIREMENTS:\n"
                "1. Return ONLY a JSON object with a single key 'dialogue' containing an array of arrays\n"
                "2. Each inner array must have exactly 2 elements: speaker label and dialogue text\n"
                "3. Speaker labels must be either 'Speaker 1' or 'Speaker 2'\n"
                "4. The conversation should be engaging and include analogies\n\n"
                "TEXT TO CONVERT:\n" + text
            ),
        },
    ]

    if provider == "openrouter":
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")
        print("Using OpenRouter API endpoint.")
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = "https://api.openai.com/v1"
        print("Using OpenAI API endpoint.")

    client = openai.OpenAI(api_key=api_key, base_url=base_url)
    
    print(f"Sending request to {base_url} to generate a podcast script...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=50000,
        response_format={"type": "json_object"}  # Force JSON response
    )

    try:
        # Parse the JSON response
        content = json.loads(response.choices[0].message.content)
        
        # Validate the JSON structure
        if not isinstance(content, dict) or 'dialogue' not in content:
            raise ValueError("Response missing 'dialogue' key")
        
        dialogue = content['dialogue']
        if not isinstance(dialogue, list):
            raise ValueError("Dialogue must be an array")
        
        # Validate and convert each dialogue entry
        transcript_list = []
        for i, entry in enumerate(dialogue):
            if not isinstance(entry, list) or len(entry) != 2:
                print(f"Skipping invalid dialogue entry {i}: {entry}")
                continue
            if entry[0] not in ["Speaker 1", "Speaker 2"]:
                print(f"Invalid speaker label in entry {i}: {entry[0]}")
                continue
            transcript_list.append(tuple(entry))
        
        if not transcript_list:
            raise ValueError("No valid dialogue entries found")
        
        # Convert to string format for storage
        script = str(transcript_list)
        
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON response from API: {e}")
        print(f"Raw response: {response.choices[0].message.content}")
        return None, None
    except Exception as e:
        print(f"Error processing response: {e}")
        return None, None

    # Save the transcript
    with open(transcript_path, "w") as f:
        f.write(script)
    print(f"Saved podcast script as {transcript_path}")
    
    return script, transcript_path


async def _generate_script_async(messages):
    response = await openai.ChatCompletion.acreate(
        model="gpt-4o-mini", messages=messages, temperature=0.7, max_tokens=20000
    )
    return response["choices"][0]["message"]["content"]


if __name__ == "__main__":
    # For example, to generate a podcast script from the PDF using OpenRouter or OpenAI:
    transcript, transcript_path = generate_podcast_script(pdf, provider="openrouter")
    # Use the transcript to generate and save the audio. The output file is stored in the same folder.
    audio_output = transcript_path.replace(".txt", ".wav")
    generate_audio_from_script(transcript, output_file=audio_output)
