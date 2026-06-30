import { useEffect, useRef, useState } from "react";
import { Sidebar } from "./components/Sidebar";
import { Composer } from "./components/Composer";
import { Message, TypingBubble } from "./components/Message";
import { planTrip } from "./lib/api";
import { useChats } from "./lib/useChats";

const SUGGESTIONS = [
  { icon: "🏖️", label: "3 days in Goa\nunder ₹15,000", prompt: "Plan a 3 day trip to Goa for 2 with a budget of 15000 INR" },
  { icon: "🏔️", label: "Manali trip\nfrom Delhi", prompt: "Plan a 5 day trip from Delhi to Manali for 2" },
  { icon: "🕌", label: "Golden Triangle\nDelhi–Agra–Jaipur", prompt: "Plan a 6 day Golden Triangle trip: Delhi, Agra and Jaipur for 2" },
  { icon: "🌴", label: "Kerala backwaters\n5 days", prompt: "Plan a 5 day Kerala backwaters trip for 2 travelers" },
];

let idSeq = 0;
const nextId = () => `m${++idSeq}`;

export default function App() {
  const chats = useChats();
  const [loading, setLoading] = useState(false);
  const [dark, setDark] = useState(false);
  const [navOpen, setNavOpen] = useState(false);
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
      chats.appendMessage({
        id: nextId(),
        role: "assistant",
        text: res.natural_language,
        summary: res.summary,
      });
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
  const closeNav = () => setNavOpen(false);

  return (
    <div className={`app ${dark ? "dark" : ""} ${navOpen ? "nav-open" : ""}`}>
      <Sidebar
        conversations={chats.conversations}
        folders={chats.folders}
        currentId={chats.currentId}
        onNewChat={() => { chats.newChat(); closeNav(); }}
        onSelect={(id) => { chats.selectChat(id); closeNav(); }}
        onCreateFolder={chats.createFolder}
        onMoveChat={chats.moveChat}
        onDeleteChat={chats.deleteChat}
        onDeleteFolder={chats.deleteFolder}
      />
      <div className="backdrop" onClick={closeNav} />

      <main className="main">
        <div className="topbar">
          <button
            className="nav-toggle"
            onClick={() => setNavOpen(true)}
            aria-label="Open menu"
          >
            ☰
          </button>
          <button
            className="theme-toggle"
            onClick={() => setDark((d) => !d)}
            aria-label="Toggle theme"
          >
            {dark ? "🌙" : "☀"}
          </button>
        </div>

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
