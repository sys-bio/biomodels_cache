# BioModels Cache System Design Document

## 1. Problem Statement and Use Cases

### Problem Statement

The BioModels Cache System addresses the need for efficient access to biological models from the BioModels database. The current approach of directly querying the BioModels API for each request is inefficient, especially for applications that frequently access the same models. This system provides a caching mechanism to improve performance and reduce API calls.
The BioModels Cache System aims to provide efficient local access to BioModels metadata, reducing API calls and improving response times for applications that frequently access BioModels data.

### Use Cases

#### UC1: Search for BioModels

**Actor**: Application Developer/End User  
**Description**: The user searches for BioModels using keywords, partial IDs, or filters with optional pagination. The system returns models ranked by relevance.
**Preconditions**: Cache is initialized and populated.  
**Main Flow**:

1. User submits a search query (e.g., model title, partial model ID, author, journal).
2. System performs a relevance-ranked search in the cache:
   a. Exact model ID matches are prioritized (e.g., entering 5 returns BIOMD0000000005 first).
   b. Partial matches are then listed by descending relevance.
3. Search results include model ID, title, authors, and other metadata.
4. User browses or selects relevant models.

#### UC2: Retrieve BioModel by ID

**Actor**: Application Developer/End User  
**Description**: The user retrieves a specific BioModel by its ID or partial ID.
**Preconditions**: Cache is initialized and contains the requested model.  
**Main Flow**:

1. User submits a request with a BioModel ID (e.g., BIOMD0000000052) or partial ID (e.g., 52).
2. System handles both formats:
   a. For full IDs, directly retrieves the model
   b. For numeric IDs, converts to full format (e.g., 52 → BIOMD0000000052)
3. System retrieves the model from the cache
4. Model metadata and associated files are returned.

**Notes:**

- The system supports both full IDs (e.g., BIOMD0000000052) and numeric IDs (e.g., 52)
- Numeric IDs are automatically converted to the full format
- This behavior is consistent with the search functionality in UC1

#### UC3: Update Cache

**Actor**: System Administrator/GitHub Actions  
**Description**: The cache is updated with new or modified models from the BioModels API.  
**Preconditions**: Admin has appropriate permissions or GitHub Actions is configured.  
**Main Flow**:

1. Update is triggered either:
   a. Manually by an administrator
   b. Automatically via GitHub Actions (e.g., daily/weekly)
2. System connects to the BioModels API
3. System fetches updated model data with a progress indicator
4. System updates the local cache
5. If running via GitHub Actions:
   a. Changes are committed to the repository
   b. A pull request is created for review
6. Admin reviews and approves changes (if via GitHub Actions)

## 2. Components and Objects

### 2.1 Client API Components

#### BiomodelsCacheClient

**Purpose**: Main client interface for accessing the BioModels cache.

**Properties**:

- `storage`: CacheStorage - The storage implementation being used

**Methods**:

- `constructor(config: CacheConfig)`: Initializes the client with the specified configuration
- `initialize(): Promise<void>`: Initializes the client and storage
- `getByKey(modelId: string): Promise<CacheEntry | null>`: Retrieves a model by ID (supports both full and numeric IDs)
- `search(query: SearchQuery): Promise<SearchResult[]>`: Searches for models

#### CacheConfig

**Purpose**: Configuration for the BiomodelsCacheClient.

**Properties**:

- `path: string` - Path to the cache directory
- `accessType: 'local' | 'github' | 'remote'` - Type of storage to use
- `githubRepo?: string` - GitHub repository (required if accessType is 'github')
- `branch?: string` - GitHub branch (default: 'main')
- `cacheFileName?: string` - Name of the cache file (default: 'biomodels_cache.json')

#### CacheEntry

**Purpose**: Represents a cached BioModel.

**Properties**:

- `modelId: string` - BioModel ID
- `files: Record<string, string>` - Files associated with the model
- `metadata: ModelMetadata` - Metadata about the model

#### ModelMetadata

**Purpose**: Metadata about a BioModel.

**Properties**:

- `name: string` - Name of the model
- `curators: string[]` - Curators who added the model to BioModels
- `publicationAuthors: string[]` - Authors of the original publication
- `title: string` - Title of the model
- `synopsis: string` - Synopsis of the model
- `citation: string | null` - Citation for the model
- `date: string` - Publication date
- `journal: string` - Journal where the model was published
- `lastUpdated: string` - Last updated timestamp

#### SearchQuery

**Purpose**: Parameters for searching models.

**Properties**:

- `query: string` - Search query string
- `filters?: SearchFilters` - Optional filters
- `page?: number` - Page number (1-based)
- `pageSize?: number` - Number of results per page

#### SearchFilters

**Purpose**: Filters for search results.

**Properties**:

- `authors?: string[]` - Filter by authors (both curators and publication authors)
- `dateRange?: DateRange` - Filter by date range
- `journals?: string[]` - Filter by journals

#### SearchResult

**Purpose**: Result of a search operation.

**Properties**:

- `modelId: string` - BioModel ID
- `score: number` - Relevance score
- `matches: Match[]` - Matching snippets
- `metadata: ModelMetadata` - Model metadata

#### Match

**Purpose**: Matching snippet in a search result.

**Properties**:

- `field: string` - Field that matched
- `snippet: string` - Matching text snippet

#### CacheStorage

**Purpose**: Interface for cache storage implementations.

**Methods**:

- `initialize(): Promise<void>`: Initializes the storage
- `getEntry(modelId: string): Promise<CacheEntry | null>`: Gets a cache entry by ID
- `saveEntry(entry: CacheEntry): Promise<void>`: Saves a cache entry
- `deleteEntry(modelId: string): Promise<void>`: Deletes a cache entry
- `search(query: SearchQuery): Promise<SearchResult[]>`: Searches for cache entries

### 2.2 Storage Implementations

#### LocalFileStorage

**Purpose**: Local file storage implementation for the cache.

**Properties**:

- `basePath: string` - Path to the cache directory
- `cacheFileName: string` - Name of the cache file

**Methods**:

- `constructor(basePath: string, cacheFileName?: string)`: Initializes the storage with the specified path
- `initialize(): Promise<void>`: Creates the cache directory if it doesn't exist
- `getEntry(modelId: string): Promise<CacheEntry | null>`: Retrieves a cache entry by ID
- `saveEntry(entry: CacheEntry): Promise<void>`: Saves a cache entry
- `deleteEntry(modelId: string): Promise<void>`: Deletes a cache entry
- `search(query: SearchQuery): Promise<SearchResult[]>`: Searches for cache entries
- `calculateSearchScore(entry: CacheEntry, query: SearchQuery): number`: Calculates search score
- `findMatches(entry: CacheEntry, query: SearchQuery): Match[]`: Finds matching snippets

### 2.3 Admin API Components

#### CacheManager

**Purpose**: Manages the BioModels cache.

**Properties**:

- `cache_dir: str` - Path to the cache directory
- `cache_file: str` - Path to the cache file
- `api: BioModelsAPI` - BioModels API client

**Methods**:

- `__init__(cache_dir: str, cache_file: str = "biomodels_cache.json")`: Initializes the cache manager
- `update_cache(progress_callback: Optional[Callable[[int, int], None]] = None) -> None`: Updates the cache with the latest models from the BioModels API
- `get_model(model_id: str) -> Optional[Dict[str, Any]]`: Gets a model by ID
- `search_models(query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]`: Searches for models
- `export_json(output_path: str) -> None`: Exports the cache to a JSON file
- `import_json(input_path: str) -> None`: Imports a JSON file into the cache

#### BioModelsAPI

**Purpose**: Interfaces with the BioModels API.

**Methods**:

- `__init__()`: Initializes the API client
- `get_models(progress_callback: Optional[Callable[[int, int], None]] = None) -> List[Dict[str, Any]]`: Gets all models with progress indication
- `get_model(model_id: str) -> Dict[str, Any]`: Gets a specific model by ID, including all associated files

## 3. Implementation Details

### 3.1 Client API Implementation

The client API is implemented in TypeScript and provides a clean interface for accessing the BioModels cache. The main components are:

1. **BiomodelsCacheClient**: The main client class that provides methods for accessing the cache.
2. **CacheStorage**: An interface that defines the methods that storage implementations must implement.
3. **LocalFileStorage**: A concrete implementation of the CacheStorage interface that stores the cache in the local file system.

The client API is designed to be easy to use and extend. It supports different storage backends (local, GitHub, remote) and provides a consistent interface regardless of the storage backend.

### 3.2 Admin API Implementation

The admin API is implemented in Python and provides tools for managing the BioModels cache. The main components are:

1. **CacheManager**: A class that manages the BioModels cache, including updating the cache and searching for models.
2. **BioModelsAPI**: A class that interfaces with the BioModels API, including fetching models with progress indication.

The admin API is designed to be used both programmatically and from the command line. It provides a simple interface for common tasks and can be extended for more complex scenarios.

### 3.3 Storage Implementation

The storage implementation is responsible for storing and retrieving the cache. The current implementation is LocalFileStorage, which stores the cache in the local file system. The cache is stored as a single JSON file (`biomodels_cache.json`) that contains all models.

The storage implementation is designed to be pluggable, allowing different storage backends to be used without changing the client API. This makes it easy to switch between different storage backends or to implement new storage backends.

### 3.4 Search Implementation

The search implementation is responsible for searching the cache for models that match a query. The current implementation uses a simple scoring system that weights matches in different fields:

- Title matches: 3 points
- Author matches (both curators and publication authors): 2 points
- Synopsis matches: 1 point

The search implementation also supports filtering by authors, journals, and date ranges. The results are sorted by relevance score and paginated.

### 3.5 Cache Update Implementation

The cache update implementation is responsible for fetching models from the BioModels API and updating the local cache. The implementation includes:

1. **Progress Indication**: A callback function that reports progress during the update process.
2. **Single JSON File**: The cache is stored as a single JSON file (`biomodels_cache.json`) that contains all models.
3. **Error Handling**: The implementation includes error handling for API failures and network issues.
4. **GitHub Actions Integration**: The update process can be automated using GitHub Actions, with changes committed and pull requests created for review.

## 4. Conclusion

The BioModels Cache System provides an efficient and flexible solution for accessing BioModels data. The client API provides a clean interface for accessing the cache, while the admin API provides tools for managing the cache. The system is designed to be easy to use and extend, making it suitable for a wide range of applications.

## API Integration

### BioModels API

The system integrates with the BioModels API (https://www.ebi.ac.uk/biomodels/) to fetch model data. This integration requires:

1. API Endpoints Used:

   - GET /api/v1/models: List all models
   - GET /api/v1/models/{id}: Get specific model with all associated files

2. Rate Limiting:
   - Respect API rate limits
   - Implement retry logic for failed requests
   - Cache responses to minimize API calls
