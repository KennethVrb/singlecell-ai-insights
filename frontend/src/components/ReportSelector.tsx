import type { ReportSummary } from "../types";
import "./ReportSelector.css";

interface ReportSelectorProps {
  reports: ReportSummary[];
  isLoading: boolean;
  isError: boolean;
  selectedReportId: string | null;
  onSelect: (reportId: string) => void;
}

export function ReportSelector({
  reports,
  isLoading,
  isError,
  selectedReportId,
  onSelect
}: ReportSelectorProps) {
  if (isLoading) {
    return <p className="muted">Loading reports…</p>;
  }

  if (isError) {
    return (
      <div className="error-callout">
        <strong>Unable to load reports.</strong>
        <p>Please verify that the backend API is running.</p>
      </div>
    );
  }

  if (reports.length === 0) {
    return <p className="muted">No reports are currently available.</p>;
  }

  return (
    <ul className="report-list">
      {reports.map((report) => (
        <li key={report.id}>
          <button
            type="button"
            className={`report-tile ${report.id === selectedReportId ? "active" : ""}`}
            onClick={() => onSelect(report.id)}
          >
            <span className="report-title">{report.title}</span>
            <span className="report-description">{report.description}</span>
            <span className="report-artifacts">Artifacts: {report.available_artifacts.join(", ")}</span>
          </button>
        </li>
      ))}
    </ul>
  );
}
