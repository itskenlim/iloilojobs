"use client";

import { useMemo, useState } from "react";

import type { Job } from "@/lib/types";

type Props = {
  jobs: Job[];
};

export function JobBoard({ jobs }: Props) {
  const [query, setQuery] = useState("");
  const [company, setCompany] = useState("all");

  const companies = useMemo(() => {
    const names = new Set(jobs.map((j) => j.company_name).filter(Boolean));
    return Array.from(names).sort();
  }, [jobs]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return jobs.filter((job) => {
      if (company !== "all" && job.company_name !== company) return false;
      if (!q) return true;
      const hay =
        `${job.title} ${job.company_name} ${job.location ?? ""} ${job.city ?? ""}`.toLowerCase();
      return hay.includes(q);
    });
  }, [jobs, query, company]);

  return (
    <div className="board" id="jobs">
      <div className="filters">
        <label className="filter">
          <span>Search</span>
          <input
            type="search"
            placeholder="Title, company, location…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </label>
        <label className="filter">
          <span>Company</span>
          <select value={company} onChange={(e) => setCompany(e.target.value)}>
            <option value="all">All companies</option>
            {companies.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </label>
      </div>

      <p className="count">
        Showing <strong>{filtered.length}</strong> of {jobs.length} Iloilo roles
      </p>

      {filtered.length === 0 ? (
        <p className="empty">No jobs match your filters. Try clearing search.</p>
      ) : (
        <ul className="job-list">
          {filtered.map((job) => (
            <li key={job.id} className="job-row">
              <div className="job-main">
                <h2>{job.title}</h2>
                <p className="meta">
                  <span>{job.company_name}</span>
                  {(job.location || job.city) && (
                    <>
                      <span aria-hidden="true"> · </span>
                      <span>{job.location || job.city}</span>
                    </>
                  )}
                  {job.employment_type && (
                    <>
                      <span aria-hidden="true"> · </span>
                      <span>{job.employment_type}</span>
                    </>
                  )}
                </p>
              </div>
              <a
                className="apply"
                href={job.apply_url || job.source_url || "#"}
                target="_blank"
                rel="noopener noreferrer"
              >
                Apply
              </a>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
