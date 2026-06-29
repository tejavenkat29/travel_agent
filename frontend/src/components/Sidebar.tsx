interface SidebarProps {
  onNewChat: () => void;
}

const TRIPS = [
  { name: "Japan Trip", emoji: "🗼", count: 5 },
  { name: "Bali Vacation", emoji: "🌴", count: 3 },
  { name: "Europe Summer", emoji: "✈️", count: 2 },
  { name: "Weekend Getaway", emoji: "⛰️", count: 1 },
];

const HISTORY = [
  { title: "7 day trip to Japan", when: "Today" },
  { title: "Best beaches in Bali", when: "Yesterday" },
  { title: "Cheap flights to Europe", when: "May 20" },
  { title: "Visa process for Japan", when: "May 18" },
  { title: "Things to do in Paris", when: "May 16" },
];

export function Sidebar({ onNewChat }: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-icon" aria-hidden>
          ✈
        </div>
        <div>
          <div className="brand-name">TravelAI</div>
          <div className="brand-sub">Your AI Travel Agent</div>
        </div>
      </div>

      <button className="new-chat" onClick={onNewChat}>
        <span className="plus">+</span> New Chat
      </button>

      <div className="search">
        <span className="search-icon" aria-hidden>
          ⌕
        </span>
        <input placeholder="Search chats" aria-label="Search chats" />
      </div>

      <div className="section-head">
        <span>Trips</span>
        <button className="ghost-btn" aria-label="Add trip">
          +
        </button>
      </div>
      <ul className="list">
        {TRIPS.map((t) => (
          <li key={t.name} className="list-item">
            <span className="folder" aria-hidden>
              🗂
            </span>
            <span className="list-label">
              {t.name} <span aria-hidden>{t.emoji}</span>
            </span>
            <span className="count">{t.count}</span>
          </li>
        ))}
      </ul>

      <div className="section-head">
        <span>Chat History</span>
      </div>
      <ul className="list">
        {HISTORY.map((h) => (
          <li key={h.title} className="list-item">
            <span className="bubble-icon" aria-hidden>
              💬
            </span>
            <span className="list-label muted">{h.title}</span>
            <span className="when">{h.when}</span>
          </li>
        ))}
      </ul>

      <button className="view-all">View all chats ›</button>
    </aside>
  );
}
