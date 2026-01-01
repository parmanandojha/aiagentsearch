# Business Discovery & Website Audit Agent

An AI-powered agent that automatically discovers businesses in a given industry and geographic area, analyzes their websites, and generates comprehensive audit reports for sales and lead generation purposes.

## Features

- **Business Discovery**: Search for businesses using Google Maps API
- **Contact Extraction**: Automatically extract phone numbers, emails, and contact forms
- **Social Media Discovery**: Detect Instagram, Facebook, LinkedIn, Twitter, and YouTube profiles
- **Website Audit**: Comprehensive analysis including:
  - UX/Design (mobile responsiveness, navigation, CTAs)
  - Content analysis (value proposition, services, missing pages)
  - Tech stack detection (CMS, frontend frameworks, analytics)
  - Technical issues (SSL, SEO, broken links, performance)
- **Scoring System**: Generate website scores (0-10) and opportunity levels
- **Structured Output**: JSON format ready for sales workflows

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Google Maps API key:
   - Get an API key from [Google Cloud Console](https://console.cloud.google.com/google/maps-apis)
   - Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```
   - Add your API key to `.env`:
   ```
   GOOGLE_MAPS_API_KEY=your_api_key_here
   ```

## Usage

### Command Line

```bash
python agent.py --industry "restaurants" --location "New York, NY" --max-results 20
```

Options:
- `--industry`: Business industry/type (required)
- `--location`: Geographic location (required)
- `--max-results`: Maximum number of businesses (default: 20)
- `--website-required`: Only return businesses with websites
- `--api-key`: Google Maps API key (optional if set in .env)
- `--output`: Output file path (optional, prints to stdout if not provided)

### Python API

```python
from agent import BusinessDiscoveryAgent

# Initialize agent
agent = BusinessDiscoveryAgent(google_maps_api_key="your_key_here")

# Run audit
results = agent.run(
    industry="dentists",
    location="San Francisco, CA",
    max_results=10,
    website_required=False
)

# Access results
print(f"Found {results['summary']['total_businesses']} businesses")
for business in results['businesses']:
    print(f"{business['name']}: Score {business['website_score']}/10")
```

## Output Format

The agent returns a JSON structure:

```json
{
  "summary": {
    "industry": "restaurants",
    "location": "New York, NY",
    "total_businesses": 20,
    "poor_websites_percentage": 35.5,
    "top_opportunities": [...]
  },
  "businesses": [
    {
      "name": "Business Name",
      "website": "https://example.com",
      "location": "123 Main St, New York, NY",
      "contact": {
        "phone": "+1234567890",
        "email": "contact@example.com",
        "contact_form": "https://example.com/contact"
      },
      "socials": {
        "instagram": "https://instagram.com/business",
        "facebook": "...",
        "linkedin": "...",
        "twitter": "...",
        "youtube": "..."
      },
      "tech_stack": {
        "cms": "WordPress",
        "frontend": "Bootstrap",
        "analytics": ["Google Analytics"]
      },
      "issues": [
        "Missing SSL",
        "Broken links detected"
      ],
      "website_score": 6.5,
      "opportunity_level": "Digitally Mature"
    }
  ]
}
```

## Opportunity Levels

- **High Potential** (Score ≥ 7.0): Well-designed websites, may have expansion needs
- **Digitally Mature** (Score 4.0-6.9): Decent websites with some improvement opportunities
- **Needs Redesign** (Score < 4.0): Major issues, high sales opportunity

## Architecture

The codebase is organized into modular components:

- `agent.py` - Main orchestrator
- `discovery.py` - Business discovery using Google Maps API
- `contact_extractor.py` - Contact information extraction
- `social_discovery.py` - Social media profile detection
- `auditor.py` - Website audit and analysis
- `scoring.py` - Website scoring and opportunity classification
- `formatter.py` - Output formatting
- `config.py` - Configuration management

## Limitations & Considerations

1. **API Keys**: Requires Google Maps API key (free tier available)
2. **Rate Limiting**: Built-in delays to respect website servers
3. **Scraping**: Some websites may block automated access
4. **Data Accuracy**: Contact information may not always be found
5. **Legal Compliance**: Ensure compliance with robots.txt and terms of service

## Future Enhancements

- Support for additional business directories (Yelp, Bing Places)
- Enhanced performance metrics
- Competitive analysis features
- Integration with CRM systems
- Scheduled monitoring capabilities

## License

This project is provided as-is for sales and lead generation purposes.

## Support

For issues or questions, please review the code comments and ensure all dependencies are properly installed.


