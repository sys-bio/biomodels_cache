import { BioModelsCacheClient, CacheError } from "../src";
import { ModelData } from "../src/types";
import path from "path";
import fs from "fs";

const main = async (): Promise<void> => {
  // Initialize the client
  const client = new BioModelsCacheClient();
  try {
    // Get the workspace root (4 levels up from the examples directory)
    const workspaceRoot = path.resolve(__dirname, "../../../../");
    const cachePath = path.join(workspaceRoot, "cache", "biomodels_cache.json");
    console.log("Using cache path:", cachePath); // Debug log

    // Check if file exists
    if (!fs.existsSync(cachePath)) {
      throw new Error(`Cache file not found at: ${cachePath}`);
    }

    await client.initialize({
      path: cachePath,
      accessType: "local",
    });
  } catch (error) {
    if (error instanceof CacheError) {
      console.error(
        `Failed to initialize client: ${error.message} (${error.code})`
      );
    } else {
      console.error("Failed to initialize client:", error);
    }
    return;
  }

  console.log("\n=== Example 1: Get and display some models ===");
  const modelIds = ["BIOMD0000000001", "BIOMD0000000002", "BIOMD0000000003"];

  for (const modelId of modelIds) {
    console.log(`\nGetting model ${modelId}:`);
    try {
      const model = await client.getByKey(modelId);

      if (model) {
        console.log(`Model: ${model.name || "Unknown"}`);
        console.log(`Authors: ${model.authors?.join(", ") || "Unknown"}`);
        console.log(`Title: ${model.title || "Unknown"}`);
        console.log(
          `Synopsis: ${model.synopsis?.substring(0, 100) || "No synopsis"}...`
        );
      } else {
        console.log(`Model ${modelId} not found`);
      }
    } catch (error) {
      if (error instanceof CacheError) {
        console.error(
          `Error getting model ${modelId}: ${error.message} (${error.code})`
        );
      } else {
        console.error(`Error getting model ${modelId}:`, error);
      }
    }
  }

  console.log("\n=== Example 2: Search through cached models ===");
  const searchTerms = ["glycolysis"];

  for (const searchTerm of searchTerms) {
    console.log(`\nSearching for '${searchTerm}' in cached models:`);
    try {
      const models = await client.search({
        term: searchTerm,
        filters: {
          // Optional filters
          // authors: ['Smith'],
          // journals: ['Nature'],
          // dateRange: {
          //     start: '2020-01-01',
          //     end: '2023-12-31'
          // }
        },
        // limit: 5, // Limit results to 5 models
      });

      if (models.length > 0) {
        console.log(`Found ${models.length} models:`);
        models.forEach((model: ModelData, index: number) => {
          const modelId = model.id || "Unknown";
          const modelName = model.name || "Unknown";
          const authors = model.authors?.join(", ") || "Unknown";
          const title = model.title || "Unknown";
          const synopsis = model.synopsis
            ? `${model.synopsis.substring(0, 150)}...`
            : "No synopsis available";

          console.log(`\n${index + 1}. Model ID: ${modelId}`);
          console.log(`   Name: ${modelName}`);
          console.log(`   Authors: ${authors}`);
          console.log(`   Title: ${title}`);
          console.log(`   Synopsis: ${synopsis}`);
        });
      } else {
        console.log("No matching models found in cache");
      }
    } catch (error) {
      if (error instanceof CacheError) {
        console.error(
          `Error searching models: ${error.message} (${error.code})`
        );
      } else {
        console.error("Error searching models:", error);
      }
    }
  }

  console.log("\n=== Example 3: Get file descriptor ===");
  const modelId = "BIOMD0000000001"; // Example model ID
  //const fileName = "biomodels_cache";

  try {
    const descriptor = await client.getFileDescriptor(modelId);
    console.log(`\nFile information for model ${modelId}:`);
    console.log(`File path: ${descriptor.filePath}`);
    console.log(`File type: ${descriptor.fileType}`);
    console.log(`File size: ${descriptor.size} bytes`);
    console.log(`Last modified: ${descriptor.lastModified}`);
    if (descriptor.checksum) {
      console.log(`Checksum: ${descriptor.checksum}`);
    }
  } catch (error) {
    if (error instanceof CacheError) {
      console.error(
        `Failed to get file descriptor: ${error.message} (${error.code})`
      );
    } else {
      console.error("Failed to get file descriptor:", error);
    }
  }
};

// Run the example
main().catch((error) => {
  console.error("Error running example:", error);
  process.exit(1);
});
