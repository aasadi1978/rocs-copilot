import styles from "./wordmark.module.css";

/**
 * Typographic placeholder wordmark for rocs-copilot.
 * Spec §11: replace with a clean SVG/PNG once supplied.
 */
export function Wordmark() {
  return (
    <span className={styles.wordmark}>
      <span className={styles.rocs}>ROCS</span>
      <span className={styles.copilot}>copilot</span>
    </span>
  );
}
