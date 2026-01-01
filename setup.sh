#!/bin/bash
# Setup script for Business Discovery Agent

echo "Setting up Business Discovery Agent..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Setup complete!"
echo ""
echo "To use the agent:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Set up your .env file with GOOGLE_MAPS_API_KEY"
echo "3. Run: python agent.py --industry 'restaurants' --location 'New York, NY'"
echo ""


