import { useCallback, useEffect, useMemo, useState } from "react";
import type { ChatMessage, Conversation, Folder } from "./types";

const STORE_KEY = "travelai.store.v1";

interface Store {
  conversations: Conversation[];
  folders: Folder[];
}

function loadStore(): Store {
  try {
    const raw = localStorage.getItem(STORE_KEY);
    if (raw) return JSON.parse(raw) as Store;
  } catch {
    /* ignore corrupt storage */
  }
  return { conversations: [], folders: [] };
}

function uid(): string {
  // Stable-enough unique id without external deps.
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
}

function titleFrom(text: string): string {
  const t = text.trim().replace(/\s+/g, " ");
  return t.length > 48 ? `${t.slice(0, 48)}…` : t || "New chat";
}

/**
 * Conversation + folder store persisted to localStorage. Replaces the old
 * hardcoded chat history / trips with real, user-owned data.
 */
export function useChats() {
  const [store, setStore] = useState<Store>(() => loadStore());
  const [currentId, setCurrentId] = useState<string | null>(null);

  // Persist on every change.
  useEffect(() => {
    try {
      localStorage.setItem(STORE_KEY, JSON.stringify(store));
    } catch {
      /* storage full / unavailable — non-fatal */
    }
  }, [store]);

  const current = useMemo(
    () => store.conversations.find((c) => c.id === currentId) ?? null,
    [store.conversations, currentId],
  );

  const newChat = useCallback(() => setCurrentId(null), []);
  const selectChat = useCallback((id: string) => setCurrentId(id), []);

  /** Append a message to the current chat, creating one on the first message. */
  const appendMessage = useCallback(
    (msg: ChatMessage) => {
      setStore((s) => {
        const now = Date.now();
        let id = currentId;
        let conversations = s.conversations;

        if (!id || !conversations.some((c) => c.id === id)) {
          id = uid();
          const conv: Conversation = {
            id,
            title: msg.role === "user" ? titleFrom(msg.text) : "New chat",
            folderId: null,
            createdAt: now,
            updatedAt: now,
            messages: [msg],
          };
          conversations = [conv, ...conversations];
          // Defer selecting until after state set.
          queueMicrotask(() => setCurrentId(conv.id));
        } else {
          conversations = conversations.map((c) =>
            c.id === id
              ? { ...c, messages: [...c.messages, msg], updatedAt: now }
              : c,
          );
        }
        return { ...s, conversations };
      });
    },
    [currentId],
  );

  const createFolder = useCallback((name: string) => {
    const clean = name.trim();
    if (!clean) return;
    setStore((s) => ({
      ...s,
      folders: [...s.folders, { id: uid(), name: clean }],
    }));
  }, []);

  const moveChat = useCallback((convId: string, folderId: string | null) => {
    setStore((s) => ({
      ...s,
      conversations: s.conversations.map((c) =>
        c.id === convId ? { ...c, folderId } : c,
      ),
    }));
  }, []);

  const deleteChat = useCallback(
    (convId: string) => {
      setStore((s) => ({
        ...s,
        conversations: s.conversations.filter((c) => c.id !== convId),
      }));
      setCurrentId((id) => (id === convId ? null : id));
    },
    [],
  );

  const deleteFolder = useCallback((folderId: string) => {
    // Remove the folder; its chats fall back to "ungrouped".
    setStore((s) => ({
      folders: s.folders.filter((f) => f.id !== folderId),
      conversations: s.conversations.map((c) =>
        c.folderId === folderId ? { ...c, folderId: null } : c,
      ),
    }));
  }, []);

  return {
    conversations: store.conversations,
    folders: store.folders,
    currentId,
    messages: current?.messages ?? [],
    newChat,
    selectChat,
    appendMessage,
    createFolder,
    moveChat,
    deleteChat,
    deleteFolder,
  };
}
