"use client";

import { useMemo, useState } from "react";

import type { Job } from "@/lib/types";

type Props = {
  jobs: Job[];
};

function postedTimestamp(iso: string | null): number {
  if (!iso) return Number.NEGATIVE_INFINITY;
  const t = Date.parse(iso);
  return Number.isFinite(t) ? t : Number.NEGATIVE_INFINITY;
}

function formatPostedAbsolute(iso: string): string {
  try {
    return new Date(iso).toLocaleString("en-PH", {
      dateStyle: "medium",
      timeStyle: "short",
      timeZone: "Asia/Manila",
    });
  } catch {
    return iso;
  }
}

/** Relative label for list scanning; null if unparseable. */
function formatPostedRelative(iso: string | null): string | null {
  if (!iso) return null;
  const posted = Date.parse(iso);
  if (!Number.isFinite(posted)) return null;

  const now = Date.now();
  const days = Math.floor((now - posted) / (1000 * 60 * 60 * 24));

  if (days <= 0) return "Posted today";
  if (days === 1) return "Posted yesterday";
  if (days < 30) return `Posted ${days} days ago`;
  if (days < 60) return "Posted 30+ days ago";
  return "Posted over 2 months ago";
}

export function JobBoard({ jobs }: Props) {
  const [query, setQuery] = useState("");
  const [company, setCompany] = useState("all");

  const companies = useMemo(() => {
    const names = new Set(jobs.map((j) => j.company_name).filter(Boolean));
    return Array.from(names).sort();
  }, [jobs]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    const list = jobs.filter((job) => {
      if (company !== "all" && job.company_name !== company) return false;
      if (!q) return true;
      const hay =
        `${job.title} ${job.company_name} ${job.location ?? ""} ${job.city ?? ""}`.toLowerCase();
      return hay.includes(q);
    });

    return [...list].sort((a, b) => {
      const byDate = postedTimestamp(b.posted_at) - postedTimestamp(a.posted_at);
      if (byDate !== 0) return byDate;
      return a.title.localeCompare(b.title);
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
          {filtered.map((job) => {
            const postedLabel = formatPostedRelative(job.posted_at);
            return (
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
                  {job.posted_at && postedLabel ? (
                    <p
                      className="posted"
                      title={formatPostedAbsolute(job.posted_at)}
                    >
                      {postedLabel}
                    </p>
                  ) : (
                    <p className="posted posted-missing">Date not listed</p>
                  )}
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
            );
          })}
        </ul>
      )}
    </div>
  );
}
