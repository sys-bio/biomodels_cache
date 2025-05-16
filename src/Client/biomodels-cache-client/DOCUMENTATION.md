# Biomodels Cache Client Documentation

## Overview

The `biomodels-cache-client` is a TypeScript library designed to interact with the BioModels cache. It provides methods to fetch, store, and manage data related to BioModels.

## Installation

To install the package, run:

```bash
npm install biomodels-cache-client
```

## Usage

### Fetching Data

To fetch data from the BioModels cache, use the `fetchData` method:

```typescript
import { BiomodelsCacheClient } from "biomodels-cache-client";

const client = new BiomodelsCacheClient();
const data = await client.fetchData("modelId");
console.log(data);
```

### Storing Data

To store data in the BioModels cache, use the `storeData` method:

```typescript
const result = await client.storeData("modelId", { key: "value" });
console.log(result);
```

### Deleting Data

To delete data from the BioModels cache, use the `deleteData` method:

```typescript
const success = await client.deleteData("modelId");
console.log(success);
```

## Implementation Details

### How Data is Stored in the Cache

The `storeData` method serializes the provided data into JSON format and stores it in a local file system. The data is stored in a directory specified during the initialization of the `BiomodelsCacheClient`. The default path is `./cache`, and the cache file is named `biomodels_cache.json`.

### Where the Cache is Stored

The cache is stored in a local directory, which can be configured during the initialization of the `BiomodelsCacheClient`. The default path is `./cache`, and the cache file is named `biomodels_cache.json`. You can change this path by providing a custom configuration when initializing the client.

### When to Choose Which Package

- **biomodels-cache-client:** Use this package if you need to interact with the BioModels cache, such as fetching, storing, or deleting data. This package is ideal for applications that require direct access to the cache.
- **biomodels-cache-admin:** Use this package if you need to perform administrative tasks related to the BioModels cache, such as managing, monitoring, or configuring the cache. This package is ideal for applications that require administrative control over the cache.

### Different Situations for Choosing Packages

1. **Direct Interaction with Cache:**

   - If your application needs to fetch, store, or delete data from the BioModels cache, use `biomodels-cache-client`.
   - Example: A web application that displays model data to users.

2. **Administrative Tasks:**

   - If your application needs to manage, monitor, or configure the BioModels cache, use `biomodels-cache-admin`.
   - Example: A dashboard for administrators to monitor cache usage and performance.

3. **Combined Usage:**
   - If your application requires both direct interaction and administrative tasks, you can use both packages together.
   - Example: A platform that allows users to view models and administrators to manage the cache.

## Specific Examples

### Example 1: Fetching Data

```typescript
import { BiomodelsCacheClient } from "biomodels-cache-client";

const client = new BiomodelsCacheClient();
const data = await client.fetchData("modelId");
console.log(data);
```

### Example 2: Storing Data

```typescript
const result = await client.storeData("modelId", { key: "value" });
console.log(result);
```

### Example 3: Deleting Data

```typescript
const success = await client.deleteData("modelId");
console.log(success);
```

## Methods

- **fetchData(modelId: string): Promise<any>**  
  Fetches data for the specified model ID from the cache.

- **storeData(modelId: string, data: any): Promise<boolean>**  
  Stores the provided data in the cache for the specified model ID.

- **deleteData(modelId: string): Promise<boolean>**  
  Deletes data for the specified model ID from the cache.

## Testing

To run the tests, navigate to the package directory and run:

```bash
npm test
```

## License

MIT
