import { Chat } from "./components/Chat";
import { Wordmark } from "./assets/brand/Wordmark";
import styles from "./app.module.css";

export default function App() {
  return (
    <div className={styles.shell}>
      <div className={styles.topbar}>
        <span className={styles.topbarTitle}>
          ROCS Copilot
          <span className={styles.topbarSub}> · Powered by OpenAI</span>
        </span>
      </div>

      <div className={styles.body}>
        <aside className={styles.sidebar}>
          <div className={styles.sidebarBrand}>
            <Wordmark />
          </div>
          <div className={styles.navSection}>Chat</div>
          <div className={`${styles.navItem} ${styles.active}`}>
            <svg width="15" height="15" viewBox="0 0 15 15" fill="none">
              <path
                d="M1 2.5A1.5 1.5 0 012.5 1h10A1.5 1.5 0 0114 2.5v7A1.5 1.5 0 0112.5 11H8l-3 3v-3H2.5A1.5 1.5 0 011 9.5v-7z"
                stroke="currentColor"
                strokeWidth="1.2"
                fill="none"
              />
            </svg>
            ROCS Q&amp;A
          </div>
        </aside>

        <main className={styles.main}>
          <Chat />
        </main>
      </div>
    </div>
  );
}
