import { useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

type Role = "user" | "assistant";

interface Message {
  role: Role;
  content: string;
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [value, setValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function send() {
    const text = value.trim();
    if (!text) return;
    setValue("");
    setLoading(true);
    setError(null);
    const next: Message[] = [...messages, { role: 'user', content: text }];
    setMessages(next);
    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: next }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = (await res.json()) as { reply: string };
      setMessages([...next, { role: 'assistant', content: data.reply }]);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="border-b bg-white">
        <div className="mx-auto max-w-2xl px-4 py-3">
            <h1 className="text-xl font-semibold text-gray-900">demo-agent Chat</h1>
        </div>
      </header>

      <main className="mx-auto max-w-2xl px-4 py-4">
        <div className="rounded-lg border bg-white">
          <div className="h-96 overflow-y-auto p-4 space-y-3">
            {messages.length === 0 && (
              <p className="text-sm text-gray-400">Type a message to get started...</p>
            )}
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-[80%] rounded-lg px-3 py-2 text-sm ${
                    m.role === 'user'
                      ? "bg-blue-600 text-white"
                      : "bg-gray-100 text-gray-900"
                  }`}
                >
                  {m.content}
                </div>
              </div>
            ))}
            {loading && <p className='text-sm text-gray-400'>Thinking...</p>}
          </div>

            {error && (
              <div className="border-t bg-red-50 px-4 py-2 text-sm text-red-700">
                {error}
              </div>
            )}

          <div className="flex items-center gap-2 border-t p-3">
            <input
              className="flex-1 rounded-md border px-3 py-2 text-sm outline-none focus:border-blue-500"
              placeholder="Message..."
              value={value}
              onChange={(e) => setValue(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && send()}
            />
            <button
              onClick={send}
              className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
              disabled={loading}
            >
              Send
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
