"""
Example usage of the Business Discovery Agent

This script demonstrates how to use the agent programmatically
"""
from agent import BusinessDiscoveryAgent
import json

# Example 1: Basic usage
def example_basic():
    """Basic example with minimal configuration"""
    # Initialize agent (API key from .env file)
    agent = BusinessDiscoveryAgent()
    
    # Run audit
    results = agent.run(
        industry="coffee shops",
        location="San Francisco, CA",
        max_results=5
    )
    
    # Print summary
    print(json.dumps(results['summary'], indent=2))
    
    # Print first business details
    if results['businesses']:
        print("\nFirst business:")
        print(json.dumps(results['businesses'][0], indent=2))


# Example 2: With API key
def example_with_api_key():
    """Example with explicit API key"""
    agent = BusinessDiscoveryAgent(google_maps_api_key="your_api_key_here")
    
    results = agent.run(
        industry="restaurants",
        location="New York, NY",
        max_results=10,
        website_required=True  # Only businesses with websites
    )
    
    # Find high-opportunity businesses
    high_opportunity = [
        biz for biz in results['businesses']
        if biz['opportunity_level'] == 'Needs Redesign'
    ]
    
    print(f"Found {len(high_opportunity)} high-opportunity businesses")
    for biz in high_opportunity:
        print(f"- {biz['name']}: {biz['website_score']}/10")


# Example 3: Save results to file
def example_save_results():
    """Example saving results to a JSON file"""
    agent = BusinessDiscoveryAgent()
    
    results = agent.run(
        industry="dentists",
        location="Los Angeles, CA",
        max_results=15
    )
    
    # Save to file
    output_json = agent.formatter.to_json(results)
    with open('audit_results.json', 'w', encoding='utf-8') as f:
        f.write(output_json)
    
    print(f"Results saved! Found {results['summary']['total_businesses']} businesses")


if __name__ == '__main__':
    print("Business Discovery Agent - Example Usage\n")
    print("Uncomment one of the examples below to run:\n")
    print("# example_basic()")
    print("# example_with_api_key()")
    print("# example_save_results()")


