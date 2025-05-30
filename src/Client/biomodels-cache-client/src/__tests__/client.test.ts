/* eslint-disable no-restricted-syntax */
import fs from "fs";
import path from "path";
import { BioModelsCacheClient } from "../client";
import { CacheConfig, ModelData, SearchQuery } from "../types";

// Mock fs module
jest.mock("fs", () => ({
  promises: {
    stat: jest.fn(),
    readFile: jest.fn(),
  },
  existsSync: jest.fn(),
}));

describe("BioModelsCacheClient", () => {
  let client: BioModelsCacheClient;
  const mockConfig: CacheConfig = {
    path: "/test/cache",
    accessType: "local",
  };

  const mockModelData: ModelData = {
    id: "MODEL123",
    name: "Test Model",
    title: "Test Model Title",
    synopsis: "Test Model Synopsis",
    authors: ["Author 1", "Author 2"],
    journal: "Test Journal",
    date: "2024-01-01",
  };

  beforeEach(() => {
    client = new BioModelsCacheClient();
    jest.clearAllMocks();
    // Mock default file system responses
    (fs.promises.stat as jest.Mock).mockResolvedValue({
      isDirectory: () => true,
    });
    (fs.promises.readFile as jest.Mock).mockResolvedValue(JSON.stringify({}));
  });

  describe("initialize", () => {
    it("should initialize with valid config", async () => {
      await expect(client.initialize(mockConfig)).resolves.not.toThrow();
    });

    it("should throw error with invalid config", async () => {
      const invalidConfig = { ...mockConfig, path: "" };
      await expect(client.initialize(invalidConfig)).rejects.toThrow(
        "Cache path is required"
      );
    });
  });

  describe("getByKey", () => {
    beforeEach(async () => {
      await client.initialize(mockConfig);
    });

    it("should return null for non-existent model", async () => {
      const result = await client.getByKey("NONEXISTENT");
      expect(result).toBeNull();
    });

    it("should return model data for existing model", async () => {
      const cacheData = { MODEL123: mockModelData };
      (fs.promises.readFile as jest.Mock).mockResolvedValue(
        JSON.stringify(cacheData)
      );
      const result = await client.getByKey("MODEL123");
      expect(result).toEqual(mockModelData);
    });
  });

  describe("search", () => {
    beforeEach(async () => {
      await client.initialize(mockConfig);
    });

    it("should return matching models", async () => {
      const cacheData = {
        MODEL123: mockModelData,
        MODEL456: { ...mockModelData, id: "MODEL456", name: "Different Model" },
      };
      (fs.promises.readFile as jest.Mock).mockResolvedValue(
        JSON.stringify(cacheData)
      );

      const searchQuery: SearchQuery = {
        term: "Model",
      };

      const results = await client.search(searchQuery);
      expect(results).toHaveLength(2);
      const ids = results.map((r) => r.id);
      expect(ids).toContain("MODEL123");
      expect(ids).toContain("MODEL456");
    });

    it("should apply filters correctly", async () => {
      const cacheData = {
        MODEL123: mockModelData,
        MODEL456: {
          ...mockModelData,
          id: "MODEL456",
          authors: ["Different Author"],
        },
      };
      (fs.promises.readFile as jest.Mock).mockResolvedValue(
        JSON.stringify(cacheData)
      );

      const searchQuery: SearchQuery = {
        term: "Test",
        filters: {
          authors: ["Author 1"],
        },
      };

      const results = await client.search(searchQuery);
      expect(results).toHaveLength(1);
      expect(results[0].id).toBe("MODEL123");
    });
  });

  describe("getFileDescriptor", () => {
    beforeEach(async () => {
      await client.initialize(mockConfig);
    });

    it("should return file descriptor for existing file", async () => {
      (fs.existsSync as jest.Mock).mockReturnValue(true);
      (fs.promises.stat as jest.Mock).mockResolvedValue({
        size: 1024,
        mtime: new Date("2024-01-01"),
      });

      const descriptor = await client.getFileDescriptor("MODEL123");
      expect(descriptor).toEqual({
        modelId: "MODEL123",
        filePath: expect.any(String),
        fileType: "json",
        size: 1024,
        lastModified: expect.any(Date),
      });
    });

    it("should throw error for non-existent file", async () => {
      (fs.existsSync as jest.Mock).mockReturnValue(false);
      await expect(client.getFileDescriptor("NONEXISTENT")).rejects.toThrow(
        "No file found for model"
      );
    });
  });
});
