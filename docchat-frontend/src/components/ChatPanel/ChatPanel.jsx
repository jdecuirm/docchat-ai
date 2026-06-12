import MessageList from "./MessageList";
import StreamingIndicator from "./StreamingIndicator";
import ChatInput from "./ChatInput";

export default function ChatPanel({ messages, streaming, onSend }) {
  return (
    <div className="flex-1 flex flex-col min-h-0 bg-surface">
      <MessageList messages={messages} />
      {streaming && <StreamingIndicator />}
      <ChatInput onSend={onSend} streaming={streaming} />
    </div>
  );
}
