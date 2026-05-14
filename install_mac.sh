#!/bin/bash
set -e

echo "--- Starting Audio/OBD Environment Installation (macOS) ---"
echo

# 1. Check if Python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 not found. Install it via Homebrew: brew install python3"
    exit 1
fi

# 2. Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "ERROR: requirements.txt not found in current directory."
    exit 1
fi

# 3. Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment .venv..."
    python3 -m venv .venv || {
        echo "ERROR: Failed to create virtual environment."
        exit 1
    }
else
    echo "Virtual environment already exists."
fi

# 4. Activate environment and install dependencies
echo "Activating virtual environment..."
source .venv/bin/activate || {
    echo "ERROR: Failed to activate virtual environment."
    exit 1
}

echo "Upgrading pip..."
pip install --upgrade pip || {
    echo "ERROR: Failed to upgrade pip."
    exit 1
}

echo "Installing requirements..."
pip install -r requirements.txt || {
    echo "ERROR: Failed to install dependencies."
    exit 1
}

echo
echo "--- Installation completed successfully! ---"
echo "To start the project, activate the environment with: source .venv/bin/activate"
echo