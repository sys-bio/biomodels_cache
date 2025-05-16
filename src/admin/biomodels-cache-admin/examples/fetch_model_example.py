"""
Example script to fetch and display the details of a model from the cache.
"""
import os
import sys
from biomodels_cache_admin.cache import CacheManager

def main():
    # Initialize the cache manager
    cache_dir = "./cache"
    cache_manager = CacheManager(cache_dir=cache_dir)
    
    # Fetch a model
    model_id = "BIOMD0000001080"
    model = cache_manager.get_model(model_id)
    
    if model:
        print(f"Model: {model['name']}")
        print(f"Authors: {', '.join(model['authors'])}")
        print(f"Title: {model['title']}")
        print(f"Synopsis: {model['synopsis']}")
        print(f"Journal: {model['journal']}")
        print(f"Date: {model['date']}")
    else:
        print(f"Model {model_id} not found in cache")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 