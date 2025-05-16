import os
import json
import requests

def initialize_cache():
    # Create cache directory if it doesn't exist
    cache_dir = "./cache"
    os.makedirs(cache_dir, exist_ok=True)
    
    # Path to the cache file
    cache_file = os.path.join(cache_dir, "biomodels_cache.json")
    
    # Initialize empty cache
    cache = {}
    
    # Save empty cache to file
    with open(cache_file, 'w') as f:
        json.dump(cache, f, indent=2)
    
    print(f"Cache initialized at: {cache_file}")
    print("The cache file has been created and is ready to be populated with data.")

if __name__ == "__main__":
    initialize_cache() 