# Quick Start Guide

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Set Up API Key

Create a `.env` file in the project root:

```bash
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

Get your API key from: https://console.cloud.google.com/google/maps-apis

## 3. Run the Agent

### Command Line

```bash
python agent.py --industry "restaurants" --location "New York, NY" --max-results 10
```

### Python Script

```python
from agent import BusinessDiscoveryAgent

agent = BusinessDiscoveryAgent()
results = agent.run(
    industry="coffee shops",
    location="San Francisco, CA",
    max_results=5
)

print(results['summary'])
```

## Output

Results are returned as JSON with:
- Summary statistics
- Detailed business information
- Contact details
- Social media links
- Tech stack analysis
- Website scores and opportunity levels

See `README.md` for full documentation.


