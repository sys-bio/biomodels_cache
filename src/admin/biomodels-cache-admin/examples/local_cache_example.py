"""
Example script demonstrating local cache usage for BioModels.
"""
import os
import sys
from pathlib import Path
from biomodels_cache_admin.cache import CacheManager

def main():
    # Initialize cache manager with local storage
    cache_dir = "./cache"
    cache_path = os.path.join(cache_dir, "BiomodelCache.json")
    print(f"Using cache directory: {cache_dir}")
    print("Cache file exists:", os.path.exists(cache_path))
    print("Cache file path:", cache_path)
    
    try:
        cache_manager = CacheManager(cache_dir=cache_dir)
        print("Cache manager initialized successfully")
        print("Loaded cache keys (first 5):", list(cache_manager.cache.keys())[:5])
        
        # Example: Get a specific model
        model_id = "BIOMD0000000001"
        print(f"\nFetching model {model_id}...")
        model = cache_manager.get_model(model_id)
        if model:
            print(f"Model {model_id} details:")
            print(f"Name: {model.get('name', 'N/A')}")
            print(f"Publication: {model.get('publication', 'N/A')}")
        else:
            print(f"Model {model_id} not found in cache")
        
        # Example: List all models in cache
        print("\nListing all models in cache:")
        for model_id in list(cache_manager.cache.keys())[:10]:
            print(f"- {model_id}")
        if len(cache_manager.cache) > 10:
            print(f"... and {len(cache_manager.cache) - 10} more")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 