import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { ChatMessage } from "../lib/types";

export function Message({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";
  return (
    <div className={`msg ${isUser ? "msg-user" : "msg-assistant"}`}>
      <div className={`bubble ${message.error ? "bubble-error" : ""}`}>
        {isUser ? (
          <p>{message.text}</p>
        ) : (
          <div className="markdown">
            <Markdown remarkPlugins={[remarkGfm]}>{message.text}</Markdown>
          </div>
        )}
      </div>
    </div>
  );
}

export function TypingBubble() {
  return (
    <div className="msg msg-assistant">
      <div className="bubble">
        <div className="typing" aria-label="Planning your trip">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>
  );
}
