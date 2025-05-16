# Biomodels Cache Admin Documentation

## Overview

The `biomodels-cache-admin` is a TypeScript library designed for administrative tasks related to the BioModels cache. It provides methods to manage, monitor, and configure the cache.

## Installation

To install the package, run:

```bash
npm install biomodels-cache-admin
```

## Usage

### Managing the Cache

To manage the cache, use the `manageCache` method:

```typescript
import { BiomodelsCacheAdmin } from "biomodels-cache-admin";

const admin = new BiomodelsCacheAdmin();
const result = await admin.manageCache("action", { key: "value" });
console.log(result);
```

### Monitoring the Cache

To monitor the cache, use the `monitorCache` method:

```typescript
const status = await admin.monitorCache();
console.log(status);
```

### Configuring the Cache

To configure the cache, use the `configureCache` method:

```typescript
const success = await admin.configureCache({ setting: "value" });
console.log(success);
```

## Implementation Details

### How Data is Stored in the Cache

The `manageCache` method serializes the provided data into JSON format and stores it in a local file system. The data is stored in a directory specified during the initialization of the `BiomodelsCacheAdmin`. The default path is `./cache`, and the cache file is named `biomodels_cache.json`.

### Where the Cache is Stored

The cache is stored in a local directory, which can be configured during the initialization of the `BiomodelsCacheAdmin`. The default path is `./cache`, and the cache file is named `biomodels_cache.json`. You can change this path by providing a custom configuration when initializing the admin.

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

### Example 1: Managing the Cache

```typescript
import { BiomodelsCacheAdmin } from "biomodels-cache-admin";

const admin = new BiomodelsCacheAdmin();
const result = await admin.manageCache("action", { key: "value" });
console.log(result);
```

### Example 2: Monitoring the Cache

```typescript
const status = await admin.monitorCache();
console.log(status);
```

### Example 3: Configuring the Cache

```typescript
const success = await admin.configureCache({ setting: "value" });
console.log(success);
```

## Methods

- **manageCache(action: string, options: any): Promise<any>**  
  Manages the cache based on the specified action and options.

- **monitorCache(): Promise<any>**  
  Monitors the current status of the cache.

- **configureCache(config: any): Promise<boolean>**  
  Configures the cache with the provided settings.

## Testing

To run the tests, navigate to the package directory and run:

```bash
npm test
```

## License

MIT
