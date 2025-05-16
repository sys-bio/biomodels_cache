import pytest
from unittest.mock import patch, MagicMock
from biomodels_cache_admin.api import BioModelsAPI
import requests

@pytest.fixture
def mock_response():
    mock = MagicMock()
    mock.json.return_value = {
        "models": [
            {"id": "BIOMD0000000001", "name": "Test Model 1"},
            {"id": "BIOMD0000000002", "name": "Test Model 2"}
        ],
        "total": 2
    }
    mock.raise_for_status.return_value = None
    return mock

@pytest.fixture
def mock_model_response():
    mock = MagicMock()
    mock.json.return_value = {
        "id": "BIOMD0000000001",
        "name": "Test Model 1",
        "title": "Test Title",
        "curators": ["Curator 1"],
        "publicationAuthors": ["Author 1"],
        "synopsis": "Test synopsis",
        "citation": "Test citation",
        "date": "2020-01-01",
        "journal": "Test Journal",
        "lastUpdated": "2023-01-01"
    }
    mock.raise_for_status.return_value = None
    return mock

@pytest.fixture
def mock_files_response():
    mock = MagicMock()
    mock.json.return_value = {
        "files": {
            "model.xml": "content1",
            "model.sbml": "content2"
        }
    }
    mock.raise_for_status.return_value = None
    return mock

def test_get_models(mock_response):
    with patch('requests.Session.get', return_value=mock_response):
        api = BioModelsAPI()
        models = api.get_models()
        
        assert len(models) == 2
        assert models[0]["id"] == "BIOMD0000000001"
        assert models[1]["id"] == "BIOMD0000000002"

def test_get_models_with_progress(mock_response):
    progress_data = []
    def progress_callback(current, total):
        progress_data.append((current, total))
    
    with patch('requests.Session.get', return_value=mock_response):
        api = BioModelsAPI()
        models = api.get_models(progress_callback)
        
        assert len(progress_data) == 1  # Only called once with total count
        assert progress_data[0] == (2, 2)  # 2 models out of 2 total

def test_get_model(mock_model_response, mock_files_response):
    with patch('requests.Session.get', side_effect=[mock_model_response, mock_files_response]):
        api = BioModelsAPI()
        model = api.get_model("1")  # Test numeric ID
        
        assert model["id"] == "BIOMD0000000001"
        assert model["name"] == "Test Model 1"
        assert "files" in model
        assert model["files"]["files"]["model.xml"] == "content1"

def test_get_model_full_id(mock_model_response, mock_files_response):
    with patch('requests.Session.get', side_effect=[mock_model_response, mock_files_response]):
        api = BioModelsAPI()
        model = api.get_model("BIOMD0000000001")  # Test full ID
        
        assert model["id"] == "BIOMD0000000001"
        assert model["name"] == "Test Model 1"
        assert "files" in model

def test_get_models_network_error():
    with patch('requests.Session.get', side_effect=requests.exceptions.RequestException("Network error")):
        api = BioModelsAPI()
        with pytest.raises(requests.exceptions.RequestException):
            api.get_models()

def test_get_models_invalid_response():
    mock_response = MagicMock()
    mock_response.json.return_value = {"invalid": "data"}
    mock_response.raise_for_status.return_value = None
    
    with patch('requests.Session.get', return_value=mock_response):
        api = BioModelsAPI()
        models = api.get_models()
        assert models == []  # Should handle missing "models" key gracefully

def test_get_model_not_found():
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
    
    with patch('requests.Session.get', return_value=mock_response):
        api = BioModelsAPI()
        with pytest.raises(requests.exceptions.HTTPError):
            api.get_model("999999")  # Non-existent model ID

def test_get_model_invalid_id():
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
    
    with patch('requests.Session.get', return_value=mock_response):
        api = BioModelsAPI()
        with pytest.raises(requests.exceptions.HTTPError):
            api.get_model("invalid_id")  # Invalid model ID format 