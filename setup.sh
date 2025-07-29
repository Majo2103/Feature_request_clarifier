#!/bin/bash

# Create virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

echo "✅ Virtual environment ready. Run the app with:"
echo "streamlit run app.py"
