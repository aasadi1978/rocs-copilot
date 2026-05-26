import { useState } from "react";
import type { SourceChunk } from "../types/api";
import styles from "./sourcePanel.module.css";

interface Props {
  chunks: SourceChunk[];
}

export function SourcePanel({ chunks }: Props) {
  const [open, setOpen] = useState(false);
  if (chunks.length === 0) return null;
  return (
    <div className={styles.panel}>
      <button
        type="button"
        className={styles.toggle}
        onClick={() => setOpen((v) => !v)}
      >
        {chunks.length} sources {open ? "▴" : "▾"}
      </button>
      {open && (
        <ul className={styles.list}>
          {chunks.map((c) => (
            <li key={c.id} className={styles.item}>
              <span className={styles.filename}>{c.filename}</span>
              <span className={styles.page}> · p.{c.page}</span>
              <span className={styles.score}> · {c.score.toFixed(2)}</span>
              <p className={styles.snippet}>{c.snippet}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
