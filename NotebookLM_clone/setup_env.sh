#!/bin/bash
# Step 1: Install uv (if not already installed)
pip install uv

# Step 2: Create a new environment named ".venv"
uv venv

# Step 3: Activate the new environment
source .venv/bin/activate

# Step 4: Install Python dependencies
pip install "kokoro>=0.9.2" soundfile torch

# Step 5: Install espeak-ng using Homebrew (Mac users)
brew install espeak-ng

echo "Environment setup complete. To activate your environment in the future, run:"
echo "source .venv/bin/activate"