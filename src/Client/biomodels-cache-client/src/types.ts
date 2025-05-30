export interface CacheConfig {
  path: string;
  accessType: "local" | "remote";
  options?: {
    timeout?: number;
    retryAttempts?: number;
    cacheExpiry?: number;
  };
}

export interface SearchQuery {
  term: string;
  filters?: {
    authors?: string[];
    journals?: string[];
    dateRange?: {
      start: string;
      end: string;
    };
  };
  limit?: number;
  offset?: number;
}

export interface ModelData {
  id: string;
  name: string;
  title: string;
  synopsis: string;
  authors: string[];
  journal: string;
  date: string;
  [key: string]: any; // Additional model metadata
}

export interface FileDescriptor {
  modelId: string;
  filePath: string;
  fileType: string;
  size: number;
  lastModified: Date;
  checksum?: string;
}

export interface CacheClient {
  initialize(config: CacheConfig): Promise<void>;
  getByKey(key: string): Promise<ModelData | null>;
  search(query: SearchQuery): Promise<ModelData[]>;
  getFileDescriptor(modelId: string): Promise<FileDescriptor>;
}

export class CacheError extends Error {
  constructor(message: string, public code: string) {
    super(message);
    this.name = "CacheError";
  }
}
