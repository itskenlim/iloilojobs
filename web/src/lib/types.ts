export type Job = {
  id: string;
  title: string;
  company_id: string;
  company_name: string;
  location: string | null;
  city: string | null;
  province: string | null;
  employment_type: string | null;
  department: string | null;
  salary: string | null;
  salary_min: number | null;
  salary_max: number | null;
  description: string | null;
  requirements: string | null;
  posted_at: string | null;
  expires_at: string | null;
  source_url: string | null;
  apply_url: string | null;
  source: string;
  remote: boolean | null;
  raw_id: string;
  scraped_at: string;
};

export type ScrapeMetadata = {
  generated_at: string;
  providers: number;
  successful_providers: number;
  failed_providers: number;
  failed_provider_ids: string[];
  total_jobs: number;
  duplicates_removed: number;
  validation_dropped: number;
  duration_ms: number;
};

export type JobsEnvelope = {
  generated_at: string;
  job_count: number;
  companies: string[];
  jobs: Job[];
};

export interface JobRepository {
  getJobs(): Promise<Job[]>;
  getMetadata(): Promise<ScrapeMetadata>;
  getEnvelope(): Promise<JobsEnvelope>;
}
