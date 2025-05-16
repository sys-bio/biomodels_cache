# BioModels Cache Client

A TypeScript client library for accessing the BioModels cache. This package provides a clean interface for searching and retrieving models from the cache.

## Installation

```bash
npm install biomodels-cache-client
```

## Usage

### Basic Usage

```typescript
import { BiomodelsCacheClient, CacheConfig } from "biomodels-cache-client";

// Initialize the client
const config: CacheConfig = {
  path: "./cache", // Directory where the cache is stored
  accessType: "local", // Currently only 'local' is implemented
  cacheFileName: "biomodels_cache.json", // Optional, defaults to "biomodels_cache.json"
};

const client = new BiomodelsCacheClient(config);

// Initialize the client (this will load the cache)
await client.initialize();

// Get a model by ID (supports both full and numeric IDs)
const model = await client.getByKey("52"); // Will automatically convert to BIOMD0000000052
// or
const model = await client.getByKey("BIOMD0000000052");

// Search for models
const results = await client.search({
  query: "cell cycle", // Search term
  filters: {
    authors: ["John Smith"], // Optional: filter by authors
    journals: ["Nature"], // Optional: filter by journals
    dateRange: {
      // Optional: filter by date range
      start: "2020-01-01",
      end: "2023-12-31",
    },
  },
  page: 1, // Optional: page number (1-based)
  pageSize: 10, // Optional: number of results per page
});
```

### React Example

```typescript
import React, { useEffect, useState } from "react";
import {
  BiomodelsCacheClient,
  CacheConfig,
  CacheEntry,
} from "biomodels-cache-client";

const config: CacheConfig = {
  path: "./cache",
  accessType: "local",
};

const client = new BiomodelsCacheClient(config);

function ModelViewer() {
  const [model, setModel] = useState<CacheEntry | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadModel() {
      try {
        await client.initialize();
        const model = await client.getByKey("52");
        setModel(model);
      } catch (error) {
        console.error("Error loading model:", error);
      } finally {
        setLoading(false);
      }
    }

    loadModel();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (!model) return <div>Model not found</div>;

  return (
    <div>
      <h1>{model.metadata.title}</h1>
      <p>Authors: {model.metadata.publicationAuthors.join(", ")}</p>
      <p>Journal: {model.metadata.journal}</p>
      <p>{model.metadata.synopsis}</p>
    </div>
  );
}
```

### Search Example

```typescript
import { BiomodelsCacheClient, CacheConfig } from "biomodels-cache-client";

const config: CacheConfig = {
  path: "./cache",
  accessType: "local",
};

const client = new BiomodelsCacheClient(config);

async function searchModels() {
  await client.initialize();

  // Search for models with filters
  const results = await client.search({
    query: "cell cycle",
    filters: {
      authors: ["John Smith"],
      journals: ["Nature"],
      dateRange: {
        start: "2020-01-01",
        end: "2023-12-31",
      },
    },
    page: 1,
    pageSize: 10,
  });

  // Process results
  results.forEach((result) => {
    console.log(`Model ID: ${result.modelId}`);
    console.log(`Title: ${result.metadata.title}`);
    console.log(`Score: ${result.score}`);
    console.log("Matches:");
    result.matches.forEach((match) => {
      console.log(`  ${match.field}: ${match.snippet}`);
    });
    console.log("---");
  });
}
```

## API Reference

### BiomodelsCacheClient

The main class for accessing the BioModels cache.

#### Constructor

```typescript
constructor(config: CacheConfig)
```

- `config`: Configuration object for the client

#### Methods

- `initialize(): Promise<void>`

  - Initialize the client and load the cache

- `getByKey(modelId: string): Promise<CacheEntry | null>`

  - Get a model by ID
  - `modelId`: The model ID (can be full ID or numeric ID)

- `search(query: SearchQuery): Promise<SearchResult[]>`
  - Search for models
  - `query`: Search query object

### Types

#### CacheConfig

```typescript
interface CacheConfig {
  path: string;
  accessType: "local" | "github" | "remote";
  githubRepo?: string;
  branch?: string;
  cacheFileName?: string;
}
```

#### CacheEntry

```typescript
interface CacheEntry {
  modelId: string;
  files: Record<string, string>;
  metadata: ModelMetadata;
}
```

#### SearchQuery

```typescript
interface SearchQuery {
  query: string;
  filters?: SearchFilters;
  page?: number;
  pageSize?: number;
}
```

#### SearchResult

```typescript
interface SearchResult {
  modelId: string;
  score: number;
  matches: Match[];
  metadata: ModelMetadata;
}
```

## License

MIT
