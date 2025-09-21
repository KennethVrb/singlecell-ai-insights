import type {
  ArtifactReference,
  ChatMessage,
  ChatQueryResponse,
  ReportSummary
} from "./types";

const DEFAULT_BASE_URL = "/api";
const baseUrl = (import.meta.env.VITE_API_BASE_URL ?? DEFAULT_BASE_URL).replace(/\/$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  if (!path.startsWith("/")) {
    throw new Error("API request paths must start with '/' ");
  }

  const response = await fetch(`${baseUrl}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    ...init
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}

export function fetchReports(): Promise<ReportSummary[]> {
  return request<ReportSummary[]>("/reports");
}

export function fetchArtifacts(reportId: string): Promise<ArtifactReference[]> {
  return request<ArtifactReference[]>(`/reports/${reportId}/artifacts`);
}

export function submitChatQuery(
  reportId: string,
  userQuery: string,
  context: ChatMessage[]
): Promise<ChatQueryResponse> {
  return request<ChatQueryResponse>("/chat/query", {
    method: "POST",
    body: JSON.stringify({
      report_id: reportId,
      user_query: userQuery,
      conversation_context: context
    })
  });
}
