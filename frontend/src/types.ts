export interface ReportSummary {
  id: string;
  title: string;
  description: string;
  available_artifacts: string[];
}

export interface ArtifactReference {
  type: string;
  label: string;
  url: string;
}

export type ChatRole = "user" | "assistant";

export interface ChatMessage {
  role: ChatRole;
  content: string;
}

export interface ChatQueryResponse {
  answer: string;
  citations: ArtifactReference[];
  follow_up_questions?: string[];
}

export interface ChatConversationItem extends ChatMessage {
  id: string;
  citations?: ArtifactReference[];
  follow_up_questions?: string[];
}
