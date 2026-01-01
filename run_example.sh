#!/bin/bash
# Example run script for Business Discovery Agent

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the agent with example parameters
python3 agent.py \
    --industry "coffee shops" \
    --location "San Francisco, CA" \
    --max-results 5 \
    --output results.json

echo ""
echo "Results saved to results.json"


