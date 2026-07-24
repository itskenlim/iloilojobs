import { JobBoard } from "@/components/JobBoard";
import { createJobRepository } from "@/lib/job-repository";

function formatUpdated(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleString("en-PH", {
      dateStyle: "medium",
      timeStyle: "short",
      timeZone: "Asia/Manila",
    });
  } catch {
    return iso;
  }
}

function IconAggregate() {
  return (
    <svg className="step-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M4 7h16M4 12h10M4 17h7"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
      />
      <circle cx="18" cy="17" r="3" stroke="currentColor" strokeWidth="1.75" />
    </svg>
  );
}

function IconFilter() {
  return (
    <svg className="step-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M4 5h16l-6 7.5V19l-4 2v-8.5L4 5z"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function IconApply() {
  return (
    <svg className="step-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M7 17L17 7M17 7H9M17 7v8"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function IconGitHub() {
  return (
    <svg className="footer-github-icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M12 2C6.477 2 2 6.586 2 12.253c0 4.537 2.865 8.383 6.839 9.743.5.094.683-.222.683-.494 0-.243-.009-.888-.014-1.743-2.782.618-3.369-1.372-3.369-1.372-.455-1.183-1.11-1.498-1.11-1.498-.908-.636.069-.623.069-.623 1.004.072 1.533 1.057 1.533 1.057.892 1.566 2.341 1.114 2.91.852.091-.662.35-1.114.636-1.37-2.22-.26-4.555-1.14-4.555-5.074 0-1.121.39-2.038 1.029-2.756-.103-.26-.446-1.302.098-2.714 0 0 .84-.276 2.75 1.052A9.35 9.35 0 0 1 12 6.844a9.35 9.35 0 0 1 2.504.346c1.909-1.328 2.748-1.052 2.748-1.052.546 1.412.203 2.454.1 2.714.64.718 1.028 1.635 1.028 2.756 0 3.944-2.339 4.811-4.566 5.066.359.317.679.943.679 1.901 0 1.372-.012 2.477-.012 2.814 0 .274.18.593.688.492C19.138 20.633 22 16.787 22 12.253 22 6.586 17.523 2 12 2z" />
    </svg>
  );
}

export default async function HomePage() {
  const repo = createJobRepository();
  const [jobs, metadata] = await Promise.all([
    repo.getJobs(),
    repo.getMetadata(),
  ]);

  return (
    <main>
      <header className="hero">
        <div className="hero-media" role="img" aria-label="City skyline atmosphere" />
        <div className="hero-content">
          <p className="brand">Iloilo Jobs</p>
          <h1>BPO openings across Iloilo, all in one place.</h1>
          <p className="lede">
            From company career sites — filtered for Iloilo so you can browse
            jobs without switching between portals.
          </p>
          <p className="hero-hook" aria-live="polite">
            <span className="hero-hook-count">{jobs.length}</span>
            <span className="hero-hook-label">
              {jobs.length === 1 ? "Role available" : "Roles available"}
            </span>
          </p>
          <a className="cta" href="#jobs">
            Browse openings
          </a>
          <p className="updated">
            Last updated {formatUpdated(metadata.generated_at)} ·{" "}
            {metadata.successful_providers}/{metadata.providers} sources ok
          </p>
        </div>
      </header>

      <section className="how wrap" aria-labelledby="how-heading">
        <h2 id="how-heading">How it works</h2>
        <p className="section-lede">
          Fresh listings pulled on a schedule — always apply on the employer’s
          official page.
        </p>
        <ol className="steps">
          <li className="step">
            <IconAggregate />
            <h3>Aggregate</h3>
            <p>Pull open roles from major BPO career boards in one pass.</p>
          </li>
          <li className="step">
            <IconFilter />
            <h3>Filter to Iloilo</h3>
            <p>Iloilo and nearby sites only.</p>
          </li>
          <li className="step">
            <IconApply />
            <h3>Apply officially</h3>
            <p>Each listing links to the company’s official application flow.</p>
          </li>
        </ol>
      </section>

      <section className="board-section wrap" aria-labelledby="jobs-heading">
        <h2 id="jobs-heading" className="board-heading">
          Open roles
        </h2>
        <p className="section-lede">Search by title or company.</p>
        <JobBoard jobs={jobs} />
      </section>

      <footer className="footer">
        <div className="footer-inner">
          <div className="footer-brand-block">
            <p className="footer-brand">Iloilo Jobs</p>
            <p className="footer-purpose">
              Aggregated BPO openings for Iloilo. Always apply on the employer’s
              official page.
            </p>
            <p className="footer-maker">Made by Jose Marie Lim</p>
          </div>
          <a
            className="footer-source"
            href="https://github.com/itskenlim/iloilojobs"
            target="_blank"
            rel="noopener noreferrer"
          >
            <IconGitHub />
            Source
          </a>
        </div>
      </footer>
    </main>
  );
}
