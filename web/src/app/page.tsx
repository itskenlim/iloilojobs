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

export default async function HomePage() {
  const repo = createJobRepository();
  const [jobs, metadata] = await Promise.all([
    repo.getJobs(),
    repo.getMetadata(),
  ]);

  return (
    <main>
      <header className="hero">
        <p className="brand">Iloilo Jobs</p>
        <h1>BPO openings across Iloilo, in one board.</h1>
        <p className="lede">
          Aggregated from company career sites — filtered to Iloilo so graduates
          can scan roles without hopping between portals.
        </p>
        <a className="cta" href="#jobs">
          Browse openings
        </a>
        <p className="updated">
          Last updated {formatUpdated(metadata.generated_at)} ·{" "}
          {metadata.total_jobs} roles · {metadata.successful_providers}/
          {metadata.providers} sources ok
        </p>
      </header>

      <JobBoard jobs={jobs} />

      <footer className="footer">
        <p>
          Not affiliated with the listed employers. Always verify openings on the
          official apply link.
        </p>
      </footer>
    </main>
  );
}
