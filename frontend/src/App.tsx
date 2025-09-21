import { useEffect, useMemo, useState } from "react";
import "./App.css";
import { ChatPanel } from "./components/ChatPanel";
import { ContextPanel } from "./components/ContextPanel";
import { ReportSelector } from "./components/ReportSelector";
import { useReports } from "./hooks/useReports";
import type { ChatConversationItem, ReportSummary } from "./types";

function resolveSelectedReport(
  reports: ReportSummary[],
  preferredId: string | null
): ReportSummary | null {
  if (!preferredId) {
    return null;
  }

  return reports.find((report) => report.id === preferredId) ?? null;
}

export default function App() {
  const { data: reports = [], isLoading, isError } = useReports();
  const [selectedReportId, setSelectedReportId] = useState<string | null>(null);
  const [conversation, setConversation] = useState<ChatConversationItem[]>([]);

  useEffect(() => {
    if (!isLoading && !isError && reports.length > 0 && !selectedReportId) {
      setSelectedReportId(reports[0].id);
    }
  }, [isLoading, isError, reports, selectedReportId]);

  const selectedReport = useMemo(
    () => resolveSelectedReport(reports, selectedReportId),
    [reports, selectedReportId]
  );

  const handleReportSelection = (reportId: string) => {
    setSelectedReportId(reportId);
    setConversation([]);
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <h1>SingleCell AI Insights</h1>
          <p className="tagline">Chat with curated nf-core/singlecell reports.</p>
        </div>
      </header>
      <main className="app-body">
        <section className="panel report-panel">
          <div className="panel-header">
            <h2>Reports</h2>
          </div>
          <div className="panel-content">
            <ReportSelector
              reports={reports}
              isLoading={isLoading}
              isError={isError}
              selectedReportId={selectedReportId}
              onSelect={handleReportSelection}
            />
          </div>
        </section>
        <section className="panel chat-panel">
          <div className="panel-header">
            <h2>Assistant</h2>
          </div>
          <div className="panel-content">
            <ChatPanel
              report={selectedReport}
              conversation={conversation}
              onConversationUpdate={setConversation}
            />
          </div>
        </section>
        <section className="panel context-panel">
          <div className="panel-header">
            <h2>Context</h2>
          </div>
          <div className="panel-content">
            <ContextPanel report={selectedReport} />
          </div>
        </section>
      </main>
    </div>
  );
}
