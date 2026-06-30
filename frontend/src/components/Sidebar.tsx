import { useMemo, useState } from "react";
import type { Conversation, Folder } from "../lib/types";

interface SidebarProps {
  conversations: Conversation[];
  folders: Folder[];
  currentId: string | null;
  onNewChat: () => void;
  onSelect: (id: string) => void;
  onCreateFolder: (name: string) => void;
  onMoveChat: (convId: string, folderId: string | null) => void;
  onDeleteChat: (convId: string) => void;
  onDeleteFolder: (folderId: string) => void;
}

function relativeWhen(ts: number): string {
  const d = new Date(ts);
  const today = new Date();
  const startOf = (x: Date) => new Date(x.getFullYear(), x.getMonth(), x.getDate()).getTime();
  const days = Math.round((startOf(today) - startOf(d)) / 86_400_000);
  if (days <= 0) return "Today";
  if (days === 1) return "Yesterday";
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

export function Sidebar({
  conversations,
  folders,
  currentId,
  onNewChat,
  onSelect,
  onCreateFolder,
  onMoveChat,
  onDeleteChat,
  onDeleteFolder,
}: SidebarProps) {
  const [query, setQuery] = useState("");
  const [activeFolder, setActiveFolder] = useState<string | null>(null);

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    return conversations.filter((c) => {
      const matchesQuery = !q || c.title.toLowerCase().includes(q);
      const matchesFolder = !activeFolder || c.folderId === activeFolder;
      return matchesQuery && matchesFolder;
    });
  }, [conversations, query, activeFolder]);

  const countFor = (folderId: string) =>
    conversations.filter((c) => c.folderId === folderId).length;

  function addFolder() {
    const name = window.prompt("New folder name (e.g. Japan Trip):");
    if (name) onCreateFolder(name);
  }

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
        <input
          placeholder="Search chats"
          aria-label="Search chats"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>

      {/* --- Folders (Trips) --- */}
      <div className="section-head">
        <span>Trips</span>
        <button className="ghost-btn" aria-label="Add folder" onClick={addFolder}>
          +
        </button>
      </div>
      <ul className="list">
        {folders.length === 0 && (
          <li className="list-empty">No folders yet — tap +</li>
        )}
        {folders.map((f) => (
          <li
            key={f.id}
            className={`list-item ${activeFolder === f.id ? "active" : ""}`}
            onClick={() => setActiveFolder((cur) => (cur === f.id ? null : f.id))}
          >
            <span className="folder" aria-hidden>
              🗂
            </span>
            <span className="list-label">{f.name}</span>
            <span className="count">{countFor(f.id)}</span>
            <button
              className="del-btn"
              aria-label="Delete folder"
              onClick={(e) => {
                e.stopPropagation();
                onDeleteFolder(f.id);
                if (activeFolder === f.id) setActiveFolder(null);
              }}
            >
              ✕
            </button>
          </li>
        ))}
      </ul>

      {/* --- Chat history --- */}
      <div className="section-head">
        <span>{activeFolder ? "In this folder" : "Chat History"}</span>
      </div>
      <ul className="list">
        {visible.length === 0 && (
          <li className="list-empty">No chats yet</li>
        )}
        {visible.map((c) => (
          <li
            key={c.id}
            className={`list-item ${currentId === c.id ? "active" : ""}`}
            onClick={() => onSelect(c.id)}
          >
            <span className="bubble-icon" aria-hidden>
              💬
            </span>
            <span className="list-label" title={c.title}>
              {c.title}
            </span>
            <span className="when">{relativeWhen(c.updatedAt)}</span>
            <select
              className="move-select"
              aria-label="Move to folder"
              value={c.folderId ?? ""}
              onClick={(e) => e.stopPropagation()}
              onChange={(e) => onMoveChat(c.id, e.target.value || null)}
            >
              <option value="">No folder</option>
              {folders.map((f) => (
                <option key={f.id} value={f.id}>
                  {f.name}
                </option>
              ))}
            </select>
            <button
              className="del-btn"
              aria-label="Delete chat"
              onClick={(e) => {
                e.stopPropagation();
                onDeleteChat(c.id);
              }}
            >
              ✕
            </button>
          </li>
        ))}
      </ul>
    </aside>
  );
}
