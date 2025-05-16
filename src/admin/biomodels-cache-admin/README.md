# BioModels Cache Admin

A Python package for managing the BioModels cache. This package provides tools for updating, searching, and managing the local cache of BioModels data.

## Installation

```bash
pip install biomodels-cache-admin
```

## Usage

### Basic Usage

```python
from biomodels_cache_admin import CacheManager

# Initialize the cache manager
cache_manager = CacheManager(
    cache_dir="./cache",  # Directory to store the cache
    cache_file="biomodels_cache.json"  # Optional, defaults to "biomodels_cache.json"
)

# Update the cache (this will fetch all models from BioModels)
def progress_callback(current: int, total: int):
    print(f"Progress: {current}/{total} models processed")

cache_manager.update_cache(progress_callback)

# Get a model by ID (supports both full and numeric IDs)
model = cache_manager.get_model("52")  # Will automatically convert to BIOMD0000000052
# or
model = cache_manager.get_model("BIOMD0000000052")

# Search for models
results = cache_manager.search_models(
    query="cell cycle",  # Search term
    filters={
        "authors": ["John Smith"],  # Optional: filter by authors
        "journals": ["Nature"],     # Optional: filter by journals
        "dateRange": {              # Optional: filter by date range
            "start": "2020-01-01",
            "end": "2023-12-31"
        }
    }
)
```

### Command Line Interface

The package also provides a command-line interface for basic operations:

```bash
# Update the cache
biomodels-cache update --cache-dir ./cache

# Get a model by ID
biomodels-cache get 52 --cache-dir ./cache

# Search for models
biomodels-cache search "cell cycle" --cache-dir ./cache --authors "John Smith" --journals "Nature"
```

### GitHub Actions Integration

To set up automatic cache updates using GitHub Actions, create a file `.github/workflows/update-cache.yml`:

```yaml
name: Update BioModels Cache

on:
  schedule:
    - cron: "0 0 * * *" # Run daily at midnight
  workflow_dispatch: # Allow manual triggering

jobs:
  update-cache:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.9"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install biomodels-cache-admin

      - name: Update cache
        run: |
          python -c "
          from biomodels_cache_admin import CacheManager
          cache_manager = CacheManager('./cache')
          cache_manager.update_cache()
          "

      - name: Commit and push changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add cache/
          git commit -m "Update BioModels cache"
          git push
```

## API Reference

### CacheManager

The main class for managing the BioModels cache.

#### Methods

- `__init__(cache_dir: str, cache_file: str = "biomodels_cache.json")`

  - Initialize the cache manager
  - `cache_dir`: Directory to store the cache
  - `cache_file`: Name of the cache file

- `update_cache(progress_callback: Optional[Callable[[int, int], None]] = None) -> None`

  - Update the cache with the latest models from BioModels
  - `progress_callback`: Optional callback function to report progress

- `get_model(model_id: str) -> Optional[Dict[str, Any]]`

  - Get a model by ID
  - `model_id`: The model ID (can be full ID or numeric ID)

- `search_models(query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]`

  - Search for models
  - `query`: Search query string
  - `filters`: Optional filters to apply

- `export_json(output_path: str) -> None`

  - Export the cache to a JSON file
  - `output_path`: Path to save the JSON file

- `import_json(input_path: str) -> None`
  - Import a JSON file into the cache
  - `input_path`: Path to the JSON file to import

## License

MIT
