import { Chat } from "./components/Chat";
import { Wordmark } from "./assets/brand/Wordmark";
import styles from "./app.module.css";

export default function App() {
  return (
    <div className={styles.shell}>
      <header className={styles.header}>
        <Wordmark />
      </header>
      <main className={styles.main}>
        <Chat />
      </main>
    </div>
  );
}
