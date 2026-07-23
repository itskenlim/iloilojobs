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
          <h1>BPO openings across Iloilo, in one board.</h1>
          <p className="lede">
            Aggregated from company career sites — filtered to Iloilo so you can
            scan roles without hopping between portals.
          </p>
          <a className="cta" href="#jobs">
            Browse openings
          </a>
          <p className="updated">
            Last updated {formatUpdated(metadata.generated_at)} ·{" "}
            {metadata.total_jobs} roles · {metadata.successful_providers}/
            {metadata.providers} sources ok
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
            <p>Keep only Iloilo and nearby sites like Pavia and Mandurriao.</p>
          </li>
          <li className="step">
            <IconApply />
            <h3>Apply officially</h3>
            <p>Each listing links out to the company’s real apply flow.</p>
          </li>
        </ol>
      </section>

      <section className="board-section wrap" aria-labelledby="jobs-heading">
        <h2 id="jobs-heading" className="board-heading">
          Open roles
        </h2>
        <p className="section-lede">
          Search by title or company. Results update when the scrape runs.
        </p>
        <JobBoard jobs={jobs} />
      </section>

      <p className="trust">
        Not affiliated with the listed employers. Always verify openings on the
        official apply link.
      </p>

      <footer className="footer">
        <div className="footer-inner">
          <p className="footer-name">Jose Marie Lim</p>
          <a
            href="https://github.com/itskenlim/iloilojobs"
            target="_blank"
            rel="noopener noreferrer"
          >
            GitHub
          </a>
        </div>
      </footer>
    </main>
  );
}
