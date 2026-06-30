import { useEffect, useState, type KeyboardEvent } from "react";
import { useSpeechRecognition } from "../lib/useSpeechRecognition";

interface ComposerProps {
  onSend: (text: string) => void;
  disabled?: boolean;
}

export function Composer({ onSend, disabled }: ComposerProps) {
  const [value, setValue] = useState("");
  const speech = useSpeechRecognition();

  // While dictating, mirror the live transcript into the input.
  useEffect(() => {
    if (speech.listening) setValue(speech.transcript);
  }, [speech.transcript, speech.listening]);

  function submit() {
    const text = value.trim();
    if (!text || disabled) return;
    if (speech.listening) speech.stop();
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

  function toggleMic() {
    if (speech.listening) speech.stop();
    else speech.start();
  }

  return (
    <div className="composer">
      <textarea
        className="composer-input"
        placeholder={
          speech.listening ? "Listening… speak now" : "Ask anything about travel..."
        }
        value={value}
        rows={1}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={onKeyDown}
        disabled={disabled}
      />
      <div className="composer-row">
        <div className="composer-tools">
          {speech.supported ? (
            <button
              className={`tool ${speech.listening ? "mic-active" : ""}`}
              aria-label={speech.listening ? "Stop dictation" : "Speak"}
              title={speech.listening ? "Stop" : "Speak your request"}
              type="button"
              onClick={toggleMic}
            >
              🎤
            </button>
          ) : (
            <span className="composer-hint">Press Enter to send</span>
          )}
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
