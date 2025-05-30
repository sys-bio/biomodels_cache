# BioModels Cache

This repository contains two main packages for working with BioModels data:

- **Client**: TypeScript client for accessing BioModels cache.
- **Admin**: TypeScript admin API for managing BioModels cache.

---

## Packages

| Package    | Path                                | Description                                                                  |
| ---------- | ----------------------------------- | ---------------------------------------------------------------------------- |
| **Client** | `src/client/biomodels-cache-client` | End-user client for searching and retrieving models from the cache.          |
| **Admin**  | `src/admin/biomodels-cache-admin`   | Admin tools for managing the cache (e.g., populating, updating, validating). |

Each package contains its own README with usage and API details.

---

## Client Package

The **Client** package provides a TypeScript API for accessing BioModels data from a local or remote cache. It supports searching, filtering, and retrieving model metadata and files.

### Features

- Search models by term, author, journal, or date range
- Retrieve model metadata by ID
- Get file descriptors for cached models
- Local and remote cache support
- TypeScript types for all API methods
- Custom error handling

### Example Use Cases

- Integrate BioModels search into a web or desktop application
- Programmatically retrieve model files for analysis
- Build custom tools for exploring BioModels data

### Quick Example

```typescript
import { BioModelsCacheClient } from "biomodels-cache-client";

const client = new BioModelsCacheClient();
await client.initialize({ path: "/path/to/cache", accessType: "local" });
const results = await client.search({ term: "glycolysis" });
console.log(results);
```

---

## Admin Package

The **Admin** package provides tools and APIs for managing the BioModels cache. This includes populating the cache, updating models, validating data integrity, and more.

### Features

- Populate the cache from remote sources
- Update and validate cached models
- Manage cache metadata and expiry
- Command-line and programmatic interfaces

### Example Use Cases

- Set up and maintain a local BioModels cache for a research group
- Automate cache updates and validation in a CI/CD pipeline
- Build admin dashboards for cache monitoring

---

## Quick Start

### Client

See [`src/client/biomodels-cache-client/README.md`](src/client/biomodels-cache-client/README.md) for installation and usage instructions.

### Admin

See [`src/admin/biomodels-cache-admin/README.md`](src/admin/biomodels-cache-admin/README.md) for admin API usage and setup.

---

## Development

```bash
# Install dependencies for all packages (if using workspaces)
npm install

# Run tests for the client package
cd src/client/biomodels-cache-client
npm test

# Run tests for the admin package
cd ../../admin/biomodels-cache-admin
npm test
```

---

## Contributing

Contributions are welcome! Please open issues or submit pull requests for bug fixes, new features, or improvements. For major changes, please open an issue first to discuss your proposal.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a pull request

---

## License

MIT
