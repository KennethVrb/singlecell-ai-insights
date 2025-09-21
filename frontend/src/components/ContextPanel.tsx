import { useArtifacts } from "../hooks/useArtifacts";
import type { ReportSummary } from "../types";
import "./ContextPanel.css";

interface ContextPanelProps {
  report: ReportSummary | null;
}

export function ContextPanel({ report }: ContextPanelProps) {
  const { data: artifacts = [], isLoading, isError } = useArtifacts(report ? report.id : null);

  if (!report) {
    return (
      <div className="context-empty">
        <p>Select a report to view its related artifacts.</p>
      </div>
    );
  }

  return (
    <div className="context-container">
      <section className="context-report">
        <h3>{report.title}</h3>
        <p>{report.description}</p>
      </section>

      <section className="context-artifacts">
        <h4>Available artifacts</h4>
        {isLoading && <p className="muted">Loading artifacts…</p>}
        {isError && (
          <div className="error-callout">
            <strong>Unable to fetch artifacts.</strong>
            <p>Confirm the backend API is reachable.</p>
          </div>
        )}
        {!isLoading && !isError && artifacts.length === 0 && (
          <p className="muted">No artifact references were found for this report.</p>
        )}
        <ul>
          {artifacts.map((artifact) => (
            <li key={artifact.url}>
              <span className="artifact-type">{artifact.type}</span>
              <a href={artifact.url} target="_blank" rel="noreferrer">
                {artifact.label}
              </a>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
