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

  return (
    <div className={styles.chat}>
      <div className={styles.messages}>
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
        />
        <button
          type="submit"
          className={styles.send}
          disabled={streaming || !draft.trim()}
        >
          Send
        </button>
      </form>
    </div>
  );
}
