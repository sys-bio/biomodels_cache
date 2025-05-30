import pytest
import os
import json
from datetime import datetime
from biomodels_cache_admin.cache import CacheManager

@pytest.fixture
def temp_cache_dir(tmp_path):
    return str(tmp_path)

@pytest.fixture
def sample_cache_data():
    return {
        "BIOMD0000000001": {
            "id": "BIOMD0000000001",
            "name": "Test Model 1",
            "title": "Test Title 1",
            "authors": ["Author 1"],
            "synopsis": "Test synopsis 1",
            "citation": "Test citation 1",
            "date": "2020-01-01",
            "journal": "Test Journal 1"
        },
        "BIOMD0000000002": {
            "id": "BIOMD0000000002",
            "name": "Test Model 2",
            "title": "Test Title 2",
            "authors": ["Author 2"],
            "synopsis": "Test synopsis 2",
            "citation": "Test citation 2",
            "date": "2021-01-01",
            "journal": "Test Journal 2"
        }
    }

def test_initialize_cache(temp_cache_dir):
    cache_manager = CacheManager(temp_cache_dir)
    cache_file = os.path.join(temp_cache_dir, "biomodels_cache.json")
    
    assert os.path.exists(cache_file)
    assert cache_manager.cache == {}

def test_load_existing_cache(temp_cache_dir, sample_cache_data):
    cache_file = os.path.join(temp_cache_dir, "biomodels_cache.json")
    with open(cache_file, "w") as f:
        json.dump(sample_cache_data, f)
    
    cache_manager = CacheManager(temp_cache_dir)
    assert cache_manager.cache == sample_cache_data

def test_update_cache(temp_cache_dir, sample_cache_data):
    cache_manager = CacheManager(temp_cache_dir)
    models = list(sample_cache_data.values())
    
    cache_manager.update_cache(models)
    assert cache_manager.cache == sample_cache_data

def test_get_model(temp_cache_dir, sample_cache_data):
    cache_file = os.path.join(temp_cache_dir, "biomodels_cache.json")
    with open(cache_file, "w") as f:
        json.dump(sample_cache_data, f)
    
    cache_manager = CacheManager(temp_cache_dir)
    
    # Test with numeric ID
    model = cache_manager.get_model("1")
    assert model["id"] == "BIOMD0000000001"
    
    # Test with full ID
    model = cache_manager.get_model("BIOMD0000000002")
    assert model["id"] == "BIOMD0000000002"

def test_search_models(temp_cache_dir, sample_cache_data):
    cache_file = os.path.join(temp_cache_dir, "biomodels_cache.json")
    with open(cache_file, "w") as f:
        json.dump(sample_cache_data, f)
    
    cache_manager = CacheManager(temp_cache_dir)
    
    # Test basic search
    results = cache_manager.search_models("Test")
    assert len(results) == 2
    
    # Test search with filters
    results = cache_manager.search_models(
        "Test",
        filters={
            "authors": ["Author 1"],
            "journals": ["Test Journal 1"],
            "dateRange": {
                "start": "2019-01-01",
                "end": "2020-12-31"
            }
        }
    )
    assert len(results) == 1
    assert results[0]["id"] == "BIOMD0000000001"

def test_export_import_json(temp_cache_dir, sample_cache_data):
    cache_manager = CacheManager(temp_cache_dir)
    cache_manager.cache = sample_cache_data
    
    # Export to a temporary file
    export_path = os.path.join(temp_cache_dir, "export.json")
    cache_manager.export_json(export_path)
    
    # Create a new cache manager and import the file
    new_cache_manager = CacheManager(temp_cache_dir)
    new_cache_manager.import_json(export_path)
    
    assert new_cache_manager.cache == sample_cache_data

def test_load_invalid_cache(temp_cache_dir):
    # Create an invalid JSON file
    cache_file = os.path.join(temp_cache_dir, "biomodels_cache.json")
    with open(cache_file, "w") as f:
        f.write("invalid json")
    
    # Should initialize empty cache when file is invalid
    cache_manager = CacheManager(temp_cache_dir)
    assert cache_manager.cache == {}

def test_export_json_permission_error(temp_cache_dir, sample_cache_data):
    cache_manager = CacheManager(temp_cache_dir)
    cache_manager.cache = sample_cache_data
    
    # Create a directory with the same name as the export file
    export_path = os.path.join(temp_cache_dir, "export.json")
    os.makedirs(export_path)
    
    with pytest.raises(OSError):
        cache_manager.export_json(export_path)

def test_import_json_not_found(temp_cache_dir):
    cache_manager = CacheManager(temp_cache_dir)
    with pytest.raises(FileNotFoundError):
        cache_manager.import_json("nonexistent.json")

def test_import_json_invalid_format(temp_cache_dir):
    cache_manager = CacheManager(temp_cache_dir)
    
    # Create an invalid JSON file
    invalid_file = os.path.join(temp_cache_dir, "invalid.json")
    with open(invalid_file, "w") as f:
        f.write("invalid json")
    
    with pytest.raises(json.JSONDecodeError):
        cache_manager.import_json(invalid_file)

def test_search_models_invalid_filters(temp_cache_dir, sample_cache_data):
    cache_file = os.path.join(temp_cache_dir, "biomodels_cache.json")
    with open(cache_file, "w") as f:
        json.dump(sample_cache_data, f)
    
    cache_manager = CacheManager(temp_cache_dir)
    
    # Test with invalid date format
    with pytest.raises(ValueError):
        cache_manager.search_models(
            "Test",
            filters={
                "dateRange": {
                    "start": "invalid-date",
                    "end": "2020-12-31"
                }
            }
        )

def test_search_models_no_results(temp_cache_dir, sample_cache_data):
    cache_file = os.path.join(temp_cache_dir, "biomodels_cache.json")
    with open(cache_file, "w") as f:
        json.dump(sample_cache_data, f)
    
    cache_manager = CacheManager(temp_cache_dir)
    
    # Test search with no matches
    results = cache_manager.search_models("nonexistent")
    assert len(results) == 0

def test_search_models_case_insensitive(temp_cache_dir, sample_cache_data):
    cache_file = os.path.join(temp_cache_dir, "biomodels_cache.json")
    with open(cache_file, "w") as f:
        json.dump(sample_cache_data, f)
    
    cache_manager = CacheManager(temp_cache_dir)
    
    # Test case-insensitive search
    results = cache_manager.search_models("test")
    assert len(results) == 2 