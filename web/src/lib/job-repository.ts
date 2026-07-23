import { readFile } from "node:fs/promises";
import path from "node:path";

import type {
  Job,
  JobRepository,
  JobsEnvelope,
  ScrapeMetadata,
} from "./types";

const DATA_DIR = path.join(process.cwd(), "public", "data");

async function readJson<T>(filename: string): Promise<T> {
  const filePath = path.join(DATA_DIR, filename);
  const text = await readFile(filePath, "utf8");
  return JSON.parse(text) as T;
}

/**
 * Reads jobs from public/data JSON files.
 * Swap this class later for a Supabase-backed repository without changing UI.
 */
export class JsonJobRepository implements JobRepository {
  async getEnvelope(): Promise<JobsEnvelope> {
    return readJson<JobsEnvelope>("jobs.json");
  }

  async getJobs(): Promise<Job[]> {
    const envelope = await this.getEnvelope();
    return envelope.jobs ?? [];
  }

  async getMetadata(): Promise<ScrapeMetadata> {
    return readJson<ScrapeMetadata>("metadata.json");
  }
}

export function createJobRepository(): JobRepository {
  return new JsonJobRepository();
}
