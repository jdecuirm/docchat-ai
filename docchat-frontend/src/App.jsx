import Sidebar from "./components/Sidebar/Sidebar";
import ChatPanel from "./components/ChatPanel/ChatPanel";
import { useDocuments } from "./hooks/useDocuments";
import { useChat } from "./hooks/useChat";

export default function App() {
  const {
    documents,
    uploading,
    error: uploadError,
    upload,
    remove,
  } = useDocuments();
  const { messages, streaming, sendMessage } = useChat();

  return (
    <div className="flex flex-col h-full bg-bg text-text-primary">
      <header className="shrink-0 flex items-center px-5 py-3 bg-white border-b border-accent-dim shadow-sm">
        <h1 className="text-accent font-bold tracking-tight text-lg">
          DocChat
          <span className="ml-1.5 text-xs font-semibold text-white bg-accent px-1.5 py-0.5 rounded-full align-middle">
            AI
          </span>
        </h1>
      </header>

      <main className="flex flex-1 min-h-0">
        <Sidebar
          documents={documents}
          uploading={uploading}
          uploadError={uploadError}
          onUpload={upload}
          onDelete={remove}
        />
        <ChatPanel
          messages={messages}
          streaming={streaming}
          onSend={sendMessage}
        />
      </main>
    </div>
  );
}
