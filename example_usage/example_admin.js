import { BiomodelsCacheAdmin } from "biomodels-cache-admin";

const admin = new BiomodelsCacheAdmin();

async function manageCache() {
  const result = await admin.manageCache("modelId1", {
    modelID: "BIOMD0000000001",
    author: "John Doe",
    title: "Sample Model 1",
    description: "This is a sample model for demonstration purposes.",
    key: "value1",
  });
  console.log("Managed cache result:", result);
}

manageCache();
