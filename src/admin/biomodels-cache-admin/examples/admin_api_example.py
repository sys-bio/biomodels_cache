"""
Example script demonstrating the BioModels API client usage.
"""
import sys
from biomodels_cache_admin.api import BioModelsAPI

def main():
    """Run example API calls."""
    api = BioModelsAPI()
    
    print("\n=== Example 1: Get a specific model ===")
    model_id = "BIOMD0000000001"  # Example model ID
    model = api.get_model(model_id)
    if model:
        print(f"Model: {model.get('name', 'Unknown')}")
        print(f"Authors: {model.get('authors', 'Unknown')}")
        print(f"Title: {model.get('title', 'Unknown')}")
        print(f"Synopsis: {model.get('synopsis', 'Unknown')[:100]}...")
        print(f"Journal: {model.get('journal', 'Unknown')}")
        print(f"Date: {model.get('date', 'Unknown')}")
    else:
        print(f"Model {model_id} not found")
    
    print("\n=== Example 2: Search for models ===")
    search_term = "glycolysis"
    print(f"Searching for models with term: {search_term}")
    models = api.get_models()
    if models:
        print(f"Found {len(models)} models")
        print("First 5 models:")
        for model in models[:5]:
            print(f"- {model.get('name', 'Unknown')}")
    else:
        print("No models found")
    
    print("\n=== Example 3: Download a model ===")
    model_id = "BIOMD0000000001"  # Example model ID
    filepath = f"./cache/{model_id}.xml"
    print(f"Downloading model {model_id} to {filepath}")
    if api.download_model(model_id, filepath):
        print("Download successful")
    else:
        print("Download failed")

if __name__ == "__main__":
    sys.exit(main()) 