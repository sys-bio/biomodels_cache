"""
Example script demonstrating the cache update functionality.
"""
import sys
import os
import requests
from biomodels_cache_admin.cache import CacheManager

def main():
    """Run cache update example."""
    # Initialize cache manager
    cache_dir = "./cache"
    cache_manager = CacheManager(cache_dir=cache_dir)
    
    print("\n=== Example: Update Cache ===")
    print(f"Cache directory: {os.path.abspath(cache_dir)}")
    
    # Check if cache file exists before update
    cache_file = os.path.join(cache_dir, "biomodels_cache.json")
    if os.path.exists(cache_file):
        print(f"Existing cache file found: {cache_file}")
        print(f"Current cache size: {os.path.getsize(cache_file)} bytes")
    else:
        print("No existing cache file found")
    
    # Test API endpoint directly first
    print("\nTesting API endpoint...")
    api_url = "https://www.ebi.ac.uk/biomodels/model/search"
    params = {"query": "*", "format": "json"}
    print(f"Requesting from: {api_url}")
    print(f"With parameters: {params}")
    
    response = requests.get(api_url, params=params)
    print(f"Response status: {response.status_code}")
    print(f"Response headers: {response.headers}")
    print(f"Response text (first 500 chars): {response.text[:500]}")
    
    # Update cache
    print("\nUpdating cache from BioModels API...")
    try:
        cache_manager.update_cache()
        print("Cache update completed")
        
        # Check cache file after update
        if os.path.exists(cache_file):
            print(f"\nNew cache file size: {os.path.getsize(cache_file)} bytes")
            print(f"Cache file location: {os.path.abspath(cache_file)}")
        else:
            print("\nError: Cache file not created after update")
            
    except Exception as e:
        print(f"\nError updating cache: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 