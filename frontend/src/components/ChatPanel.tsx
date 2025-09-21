import { type Dispatch, type SetStateAction, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { submitChatQuery } from "../api";
import type { ChatConversationItem, ChatMessage, ReportSummary } from "../types";
import "./ChatPanel.css";

interface ChatPanelProps {
  report: ReportSummary | null;
  conversation: ChatConversationItem[];
  onConversationUpdate: Dispatch<SetStateAction<ChatConversationItem[]>>;
}

const createMessageId = () => `${Date.now()}-${Math.random().toString(16).slice(2)}`;

type MutationPayload = {
  reportId: string;
  userQuery: string;
  context: ChatMessage[];
};

export function ChatPanel({ report, conversation, onConversationUpdate }: ChatPanelProps) {
  const [inputValue, setInputValue] = useState("");

  const mutation = useMutation({
    mutationFn: ({ reportId, userQuery, context }: MutationPayload) =>
      submitChatQuery(reportId, userQuery, context)
  });

  const sendPrompt = (rawValue: string) => {
    if (!report) {
      return;
    }

    const trimmed = rawValue.trim();
    if (!trimmed) {
      return;
    }

    const context: ChatMessage[] = conversation.map(({ role, content }) => ({ role, content }));
    const userMessage: ChatConversationItem = {
      id: createMessageId(),
      role: "user",
      content: trimmed
    };

    onConversationUpdate((prev) => [...prev, userMessage]);
    setInputValue("");

    mutation.mutate(
      { reportId: report.id, userQuery: trimmed, context },
      {
        onSuccess: (data) => {
          const assistantMessage: ChatConversationItem = {
            id: createMessageId(),
            role: "assistant",
            content: data.answer,
            citations: data.citations,
            follow_up_questions: data.follow_up_questions
          };
          onConversationUpdate((prev) => [...prev, assistantMessage]);
        },
        onError: (error) => {
          const assistantMessage: ChatConversationItem = {
            id: createMessageId(),
            role: "assistant",
            content: `Sorry, something went wrong: ${(error as Error).message}`
          };
          onConversationUpdate((prev) => [...prev, assistantMessage]);
        }
      }
    );
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    sendPrompt(inputValue);
  };

  const handleFollowUp = (question: string) => {
    sendPrompt(question);
  };

  if (!report) {
    return (
      <div className="empty-state">
        <p>Select a report to begin exploring insights.</p>
      </div>
    );
  }

  return (
    <div className="chat-container">
      <div className="chat-history">
        {conversation.length === 0 ? (
          <div className="empty-state">
            <p>
              Ask a question about <strong>{report.title}</strong> to start the conversation.
            </p>
            <p className="hint">Example: “Which clusters show the highest mitochondrial gene expression?”</p>
          </div>
        ) : (
          conversation.map((message) => (
            <article key={message.id} className={`chat-message ${message.role}`}>
              <header>{message.role === "user" ? "You" : "AI Assistant"}</header>
              <p>{message.content}</p>
              {message.citations && message.citations.length > 0 && (
                <ul className="citation-list">
                  {message.citations.map((citation) => (
                    <li key={`${message.id}-${citation.url}`}>
                      <a href={citation.url} target="_blank" rel="noreferrer">
                        {citation.label} ({citation.type})
                      </a>
                    </li>
                  ))}
                </ul>
              )}
              {message.follow_up_questions && message.follow_up_questions.length > 0 && (
                <div className="follow-up-group">
                  <span>Suggested follow-ups:</span>
                  <div className="follow-up-buttons">
                    {message.follow_up_questions.map((question) => (
                      <button
                        key={`${message.id}-${question}`}
                        type="button"
                        onClick={() => handleFollowUp(question)}
                        disabled={mutation.isPending}
                      >
                        {question}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </article>
          ))
        )}
      </div>
      <form className="chat-input" onSubmit={handleSubmit}>
        <textarea
          value={inputValue}
          onChange={(event) => setInputValue(event.target.value)}
          placeholder="Ask about QC metrics, cluster patterns, or differential expression…"
          rows={3}
          disabled={mutation.isPending}
        />
        <div className="chat-input-actions">
          <button type="submit" disabled={mutation.isPending || !inputValue.trim()}>
            {mutation.isPending ? "Thinking…" : "Send"}
          </button>
        </div>
      </form>
    </div>
  );
}
