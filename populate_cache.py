import sys
sys.path.insert(0, './src/admin/biomodels-cache-admin')  # Ensure local package is importable

from biomodels_cache_admin import CacheManager

def progress_callback(current, total):
    print(f"Progress: {current}/{total} models processed", end='\r')

def main():
    cache_manager = CacheManager(cache_dir="./cache")
    print("Updating cache with real BioModels data...")
    cache_manager.update_cache(progress_callback)
    print("\nCache update complete!")

if __name__ == "__main__":
    main() 