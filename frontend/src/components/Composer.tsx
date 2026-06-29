import { useState, type KeyboardEvent } from "react";

interface ComposerProps {
  onSend: (text: string) => void;
  disabled?: boolean;
}

export function Composer({ onSend, disabled }: ComposerProps) {
  const [value, setValue] = useState("");

  function submit() {
    const text = value.trim();
    if (!text || disabled) return;
    onSend(text);
    setValue("");
  }

  function onKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    // Enter sends; Shift+Enter inserts a newline.
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  }

  return (
    <div className="composer">
      <textarea
        className="composer-input"
        placeholder="Ask anything about travel..."
        value={value}
        rows={1}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={onKeyDown}
        disabled={disabled}
      />
      <div className="composer-row">
        <div className="composer-tools">
          <button className="tool" aria-label="Attach" type="button">
            📎
          </button>
          <button className="tool" aria-label="Web" type="button">
            🌐
          </button>
        </div>
        <button
          className="send"
          onClick={submit}
          disabled={disabled || !value.trim()}
          aria-label="Send"
          type="button"
        >
          ➤
        </button>
      </div>
    </div>
  );
}
