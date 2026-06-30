import { useEffect, useRef, useState } from "react";
import { Sidebar } from "./components/Sidebar";
import { Composer } from "./components/Composer";
import { Message, TypingBubble } from "./components/Message";
import { planTrip } from "./lib/api";
import { useChats } from "./lib/useChats";

const SUGGESTIONS = [
  { icon: "🧳", label: "Plan a 7-day trip\nto Japan", prompt: "Plan a 7-day trip to Japan" },
  { icon: "🏖️", label: "Best beaches\nin Bali", prompt: "Best beaches in Bali for a relaxed 5-day trip" },
  { icon: "✈️", label: "Cheapest flights\nto Europe", prompt: "Find the cheapest flights to Europe for 2 travelers" },
  { icon: "📍", label: "Top places to visit\nin Switzerland", prompt: "Top places to visit in Switzerland over 6 days" },
];

let idSeq = 0;
const nextId = () => `m${++idSeq}`;

export default function App() {
  const chats = useChats();
  const [loading, setLoading] = useState(false);
  const [dark, setDark] = useState(false);
  const threadRef = useRef<HTMLDivElement>(null);

  const messages = chats.messages;

  useEffect(() => {
    threadRef.current?.scrollTo({ top: threadRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  async function handleSend(text: string) {
    if (loading) return;
    chats.appendMessage({ id: nextId(), role: "user", text });
    setLoading(true);
    try {
      const res = await planTrip(text);
      chats.appendMessage({ id: nextId(), role: "assistant", text: res.natural_language });
    } catch (err) {
      chats.appendMessage({
        id: nextId(),
        role: "assistant",
        text: `⚠️ ${(err as Error).message}`,
        error: true,
      });
    } finally {
      setLoading(false);
    }
  }

  const empty = messages.length === 0;

  return (
    <div className={`app ${dark ? "dark" : ""}`}>
      <Sidebar
        conversations={chats.conversations}
        folders={chats.folders}
        currentId={chats.currentId}
        onNewChat={chats.newChat}
        onSelect={chats.selectChat}
        onCreateFolder={chats.createFolder}
        onMoveChat={chats.moveChat}
        onDeleteChat={chats.deleteChat}
        onDeleteFolder={chats.deleteFolder}
      />

      <main className="main">
        <button
          className="theme-toggle"
          onClick={() => setDark((d) => !d)}
          aria-label="Toggle theme"
        >
          {dark ? "🌙" : "☀"}
        </button>

        {empty ? (
          <div className="hero">
            <div className="hero-icon" aria-hidden>
              ✈
            </div>
            <h1>Hi! I&apos;m your AI Travel Agent</h1>
            <p className="hero-sub">Plan your perfect trip with me.</p>
            <div className="cards">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s.prompt}
                  className="card"
                  onClick={() => handleSend(s.prompt)}
                >
                  <span className="card-icon" aria-hidden>
                    {s.icon}
                  </span>
                  <span className="card-label">{s.label}</span>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="thread" ref={threadRef}>
            <div className="thread-inner">
              {messages.map((m) => (
                <Message key={m.id} message={m} />
              ))}
              {loading && <TypingBubble />}
            </div>
          </div>
        )}

        <div className="composer-wrap">
          <Composer onSend={handleSend} disabled={loading} />
          <div className="footer">Travel smarter. Explore better. ✨</div>
        </div>
      </main>
    </div>
  );
}
