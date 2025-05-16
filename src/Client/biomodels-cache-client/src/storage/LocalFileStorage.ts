import * as fs from "fs";
import * as path from "path";
import {
  CacheStorage,
  CacheEntry,
  SearchQuery,
  SearchResult,
  Match,
} from "../types";

export class LocalFileStorage implements CacheStorage {
  private basePath: string;
  private cacheFileName: string;
  private cache: Record<string, CacheEntry>;

  constructor(
    basePath: string,
    cacheFileName: string = "biomodels_cache.json"
  ) {
    this.basePath = basePath;
    this.cacheFileName = cacheFileName;
    this.cache = {};
  }

  async initialize(): Promise<void> {
    // Create cache directory if it doesn't exist
    await fs.promises.mkdir(this.basePath, { recursive: true });

    // Load existing cache if it exists
    const cachePath = path.join(this.basePath, this.cacheFileName);
    if (fs.existsSync(cachePath)) {
      const data = await fs.promises.readFile(cachePath, "utf-8");
      this.cache = JSON.parse(data);
    }
  }

  async getEntry(modelId: string): Promise<CacheEntry | null> {
    // Convert numeric ID to full format if needed
    if (/^\d+$/.test(modelId)) {
      modelId = `BIOMD${modelId.padStart(10, "0")}`;
    }
    return this.cache[modelId] || null;
  }

  async saveEntry(entry: CacheEntry): Promise<void> {
    this.cache[entry.modelId] = entry;
    await this._saveCache();
  }

  async deleteEntry(modelId: string): Promise<void> {
    delete this.cache[modelId];
    await this._saveCache();
  }

  async search(query: SearchQuery): Promise<SearchResult[]> {
    const results: SearchResult[] = [];
    const searchQuery = query.query.toLowerCase();

    for (const [modelId, entry] of Object.entries(this.cache)) {
      const matches: Match[] = [];
      let score = 0;

      // Check title matches
      if (entry.metadata.title.toLowerCase().includes(searchQuery)) {
        matches.push({
          field: "title",
          snippet: entry.metadata.title,
        });
        score += 3;
      }

      // Check curator matches
      for (const curator of entry.metadata.curators) {
        if (curator.toLowerCase().includes(searchQuery)) {
          matches.push({
            field: "curators",
            snippet: curator,
          });
          score += 2;
        }
      }

      // Check publication author matches
      for (const author of entry.metadata.publicationAuthors) {
        if (author.toLowerCase().includes(searchQuery)) {
          matches.push({
            field: "publicationAuthors",
            snippet: author,
          });
          score += 2;
        }
      }

      // Check synopsis matches
      if (entry.metadata.synopsis.toLowerCase().includes(searchQuery)) {
        matches.push({
          field: "synopsis",
          snippet: entry.metadata.synopsis,
        });
        score += 1;
      }

      if (matches.length > 0) {
        // Apply filters if provided
        if (query.filters && !this._applyFilters(entry, query.filters)) {
          continue;
        }

        results.push({
          modelId,
          score,
          matches,
          metadata: entry.metadata,
        });
      }
    }

    // Sort by score and apply pagination
    results.sort((a, b) => b.score - a.score);

    const page = query.page || 1;
    const pageSize = query.pageSize || 10;
    const start = (page - 1) * pageSize;
    const end = start + pageSize;

    return results.slice(start, end);
  }

  private _applyFilters(
    entry: CacheEntry,
    filters: SearchQuery["filters"]
  ): boolean {
    if (!filters) return true;

    if (filters.authors) {
      const hasAuthor = filters.authors.some(
        (author) =>
          entry.metadata.curators.includes(author) ||
          entry.metadata.publicationAuthors.includes(author)
      );
      if (!hasAuthor) return false;
    }

    if (filters.dateRange) {
      const modelDate = new Date(entry.metadata.date);
      if (
        filters.dateRange.start &&
        modelDate < new Date(filters.dateRange.start)
      ) {
        return false;
      }
      if (
        filters.dateRange.end &&
        modelDate > new Date(filters.dateRange.end)
      ) {
        return false;
      }
    }

    if (
      filters.journals &&
      !filters.journals.includes(entry.metadata.journal)
    ) {
      return false;
    }

    return true;
  }

  private async _saveCache(): Promise<void> {
    const cachePath = path.join(this.basePath, this.cacheFileName);
    await fs.promises.writeFile(cachePath, JSON.stringify(this.cache, null, 2));
  }
}
