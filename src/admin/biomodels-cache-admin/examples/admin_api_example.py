"""
Example script demonstrating the BioModels API client usage.
"""
import sys
from biomodels_cache_admin.api import BioModelsAPI

def main():
    """Run example API calls."""
    api = BioModelsAPI()
    
    print("\n=== Example 1: Get and cache some models ===")
    model_ids = ["BIOMD0000000001", "BIOMD0000000002", "BIOMD0000000003"]
    for model_id in model_ids:
        print(f"\nGetting model {model_id}:")
        model = api.get_model(model_id)
        if model:
            print(f"Model: {model.get('name', 'Unknown')}")
            print(f"Authors: {', '.join(model.get('authors', ['Unknown']))}")
            print(f"Title: {model.get('title', 'Unknown')}")
            print(f"Synopsis: {model.get('synopsis', 'Unknown')[:100]}...")
        else:
            print(f"Model {model_id} not found")
    
    print("\n=== Example 2: Search through cached models ===")
    search_terms = ["glycolysis"]
    for search_term in search_terms:
        print(f"\nSearching for '{search_term}' in cached models:")
        models = api.search_cached_models(search_term)
        if models:
            print(f"Found {len(models)} models:")
            for i, model in enumerate(models, 1):
                print(f"\n{i}. Model ID: {model.get('model_id', 'Unknown')}")
                print(f"   Name: {model.get('name', 'Unknown')}")
                print(f"   Authors: {', '.join(model.get('authors', ['Unknown']))}")
                print(f"   Title: {model.get('title', 'Unknown')}")
                if model.get('synopsis'):
                    print(f"   Synopsis: {model['synopsis'][:150]}...")
        else:
            print("No matching models found in cache")
    
    print("\n=== Example 3: Download a model ===")
    model_id = "BIOMD0000000001"  # Example model ID
    filepath = f"./cache/{model_id}.xml"
    print(f"Downloading model {model_id} to {filepath}")
    if api.download_model(model_id, filepath):
        print("Download successful")
    else:
        print("Download failed")

if __name__ == "__main__":
    main() 