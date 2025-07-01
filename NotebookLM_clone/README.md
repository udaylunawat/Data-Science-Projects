# NotebookLM-Kokoro TTS Project

This project uses [Kokoro](https://huggingface.co/hexgrad/Kokoro-82M) – a lightweight, open-weight TTS model with 82 million parameters – to create a Google NotebookLM style Text-to-Speech application.

## Why Kokoro?

- **Non-Proprietary & Open-Source:** Kokoro is best in its class as a non-proprietary model, giving you full flexibility to deploy in production environments or personal projects.
- **High Efficiency:** Despite its lightweight architecture, Kokoro delivers comparable quality to larger models while being faster and more cost-efficient.
- **Benchmarks:** According to benchmarks available on the [TTS-Arena](https://huggingface.co/spaces/TTS-AGI/TTS-Arena) page, Kokoro outperforms many closed-source models, making it the ideal choice for open deployments.
- **Easy Integration:** With simple pip and Homebrew installation for dependencies like espeak-ng, integration into Python projects is straightforward.

## Setup Instructions

### Environment Setup

This project uses the **uv** Python package manager. Follow these steps:

1. **Install uv:**

   ```bash
   pip install uv
   ```

2. **Create a new environment named `notebooklm`:**

   ```bash
   uv venv
   ```

3. **Activate the environment:**

   ```bash
   source .venv/bin/activate
   ```

4. **Install Python dependencies:**

   ```bash
   pip install "kokoro>=0.9.2" soundfile torch
   ```

5. **Install espeak-ng (Mac users):**

   ```bash
   brew install espeak-ng
   ```

### Running the Application

Once the environment is set up, run the main TTS script as follows:

```bash
python notebook_lm_kokoro.py
```

This will process the transcript text using Kokoro and output audio segments as WAV files.

## Conclusion

Kokoro’s combination of efficiency, quality, and open-access makes it the best non-proprietary TTS model available, as confirmed by recent benchmarks. Enjoy exploring and extending this project!