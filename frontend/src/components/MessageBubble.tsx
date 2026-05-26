import ReactMarkdown from "react-markdown";
import styles from "./messageBubble.module.css";

type Variant = "user" | "assistant" | "error";

interface Props {
  variant: Variant;
  content: string;
  retryable?: boolean;
  onRetry?: () => void;
}

export function MessageBubble({ variant, content, retryable, onRetry }: Props) {
  return (
    <div className={`${styles.bubble} ${styles[variant]}`}>
      {variant === "user" ? (
        <p className={styles.text}>{content}</p>
      ) : (
        <div className={styles.text}>
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>
      )}
      {variant === "error" && retryable && (
        <button type="button" className={styles.retry} onClick={onRetry}>
          Retry
        </button>
      )}
    </div>
  );
}
