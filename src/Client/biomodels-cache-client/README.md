# BioModels Cache Client

A TypeScript client library for accessing and managing the BioModels cache.

## Installation

```bash
npm install biomodels-cache-client
```

## Usage

### Basic Usage

```typescript
import { BioModelsCacheClient } from "biomodels-cache-client";

// Initialize the client
const client = new BioModelsCacheClient();
await client.initialize({
  path: "./cache",
  accessType: "local",
});

// Get a model by ID
const model = await client.getByKey("BIOMD0000000001");
console.log(model);

// Search for models
const results = await client.search({
  term: "cell cycle",
  filters: {
    authors: ["Smith"],
    journals: ["Nature"],
    dateRange: {
      start: "2020-01-01",
      end: "2023-12-31",
    },
  },
  limit: 10,
  offset: 0,
});
console.log(results);

// Get file descriptor
const descriptor = await client.getFileDescriptor("BIOMD0000000001");
console.log(descriptor);
```

## Features

- Local and remote cache access
- Key-based model retrieval
- Content-based search with filters
- File descriptor management
- Error handling and retries
- TypeScript support

## API Reference

### CacheClient

The main interface for interacting with the cache.

#### Methods

- `initialize(config: CacheConfig): Promise<void>`

  - Initializes the cache client with the specified configuration

- `getByKey(key: string): Promise<ModelData | null>`

  - Retrieves a model by its ID

- `search(query: SearchQuery): Promise<ModelData[]>`

  - Searches for models based on content and filters

- `getFileDescriptor(modelId: string): Promise<FileDescriptor>`
  - Gets file information for a model

### Configuration

```typescript
interface CacheConfig {
  path: string; // Path to the cache storage
  accessType: "local" | "remote"; // Type of cache access
  options?: {
    timeout?: number; // Request timeout in milliseconds
    retryAttempts?: number; // Number of retry attempts
    cacheExpiry?: number; // Cache expiry time in seconds
  };
}
```

### Search Query

```typescript
interface SearchQuery {
  term: string; // Search term
  filters?: {
    authors?: string[]; // Filter by authors
    journals?: string[]; // Filter by journals
    dateRange?: {
      start: string; // Start date (YYYY-MM-DD)
      end: string; // End date (YYYY-MM-DD)
    };
  };
  limit?: number; // Maximum number of results
  offset?: number; // Pagination offset
}
```

## Error Handling

The client uses a custom `CacheError` class for error handling:

```typescript
try {
  await client.getByKey("invalid-id");
} catch (error) {
  if (error instanceof CacheError) {
    console.error(`Cache error: ${error.message} (${error.code})`);
  }
}
```

## Development

### Building

```bash
npm run build
```

### Testing

```bash
npm test
```

### Linting

```bash
npm run lint
```

## License

MIT
