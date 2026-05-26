import { useCallback, useEffect, useState } from "react";
import { useChatStream } from "../hooks/useChatStream";
import type { ChatTurn } from "../types/api";
import { MessageBubble } from "./MessageBubble";
import { SourcePanel } from "./SourcePanel";
import styles from "./chat.module.css";

export function Chat() {
  const [draft, setDraft] = useState("");
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [lastQuestion, setLastQuestion] = useState<string>("");
  const { answer, sources, error, streaming, send } = useChatStream();

  const submit = useCallback(
    (question: string) => {
      setTurns((prev) => [...prev, { role: "user", content: question }]);
      setLastQuestion(question);
      void send(question, turns);
    },
    [send, turns]
  );

  useEffect(() => {
    if (!streaming && answer && !error) {
      setTurns((prev) => {
        if (prev.length === 0 || prev[prev.length - 1].role !== "user") return prev;
        return [...prev, { role: "assistant", content: answer }];
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [streaming]);

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!draft.trim() || streaming) return;
    const q = draft.trim();
    setDraft("");
    submit(q);
  };

  const onRetry = () => {
    if (lastQuestion) submit(lastQuestion);
  };

  const isEmpty = turns.length === 0 && !streaming && !error;

  return (
    <div className={styles.chat}>
      <div className={styles.messages}>
        {isEmpty && (
          <div className={styles.greeting}>
            <div className={styles.avatar}>✦</div>
            <p className={styles.greetingText}>
              Hello, I am your <strong>ROCS Copilot</strong>.
              <br />
              Ask me about error codes, routing modules, or procedures.
            </p>
          </div>
        )}

        {turns.map((t, i) => (
          <MessageBubble
            key={i}
            variant={t.role === "user" ? "user" : "assistant"}
            content={t.content}
          />
        ))}
        {streaming && answer && (
          <MessageBubble variant="assistant" content={answer + "▌"} />
        )}
        {!streaming && answer && error === null && (
          <SourcePanel chunks={sources} />
        )}
        {error && (
          <MessageBubble
            variant="error"
            content={error.message}
            retryable={error.retryable}
            onRetry={onRetry}
          />
        )}
      </div>

      <div className={styles.inputBar}>
        <form className={styles.form} onSubmit={onSubmit}>
          <textarea
            className={styles.input}
            placeholder="Ask about ROCS error codes, modules, or procedures…"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                onSubmit(e as unknown as React.FormEvent);
              }
            }}
            disabled={streaming}
            rows={1}
          />
          <button
            type="submit"
            className={styles.send}
            disabled={streaming || !draft.trim()}
            aria-label="Send"
          >
            <svg
              className={styles.sendIcon}
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </button>
        </form>
      </div>
    </div>
  );
}
