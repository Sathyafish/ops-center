import { useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL || "/api";

export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem("ops_token") || "");
  const [user, setUser] = useState(null);
  const [username, setUsername] = useState("ops.alice");
  const [password, setPassword] = useState("");
  const [question, setQuestion] = useState(
    "PaymentGateway incident — who do I contact, what's impacted, and is there an active change?"
  );
  const [mode, setMode] = useState("auto");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    if (token) {
      localStorage.setItem("ops_token", token);
    }
  }, [token]);

  async function login(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      if (!res.ok) {
        throw new Error("Login failed");
      }
      const data = await res.json();
      setToken(data.access_token);
      setUser(data.user);
      setPassword("");
    } catch {
      setError("Invalid credentials");
    } finally {
      setLoading(false);
    }
  }

  async function ask(e) {
    e.preventDefault();
    if (!token || !question.trim()) return;
    setError("");
    setLoading(true);
    const q = question.trim();
    setMessages((m) => [...m, { role: "user", text: q }]);
    try {
      const res = await fetch(`${API_BASE}/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ question: q, mode }),
      });
      if (res.status === 401) {
        setToken("");
        localStorage.removeItem("ops_token");
        throw new Error("Session expired — log in again");
      }
      if (!res.ok) {
        throw new Error("Query failed");
      }
      const data = await res.json();
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          text: data.answer,
          meta: `Route: ${data.route}`,
        },
      ]);
      setQuestion("");
    } catch (err) {
      setError(err.message || "Request failed");
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    setToken("");
    setUser(null);
    localStorage.removeItem("ops_token");
    setMessages([]);
  }

  if (!token) {
    return (
      <div className="page">
        <header>
          <h1>Ops Center GraphRAG</h1>
          <p>Incident routing, blast radius, escalation, and change correlation</p>
        </header>
        <form className="card" onSubmit={login}>
          <label>
            Username
            <select value={username} onChange={(e) => setUsername(e.target.value)}>
              <option value="ops.alice">ops.alice (lead)</option>
              <option value="ops.bob">ops.bob</option>
              <option value="ops.carol">ops.carol</option>
              <option value="ops.dave">ops.dave</option>
              <option value="ops.eve">ops.eve (oncall)</option>
            </select>
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="OpsCenter2026!"
              required
            />
          </label>
          {error && <p className="error">{error}</p>}
          <button type="submit" disabled={loading}>
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>
      </div>
    );
  }

  return (
    <div className="page">
      <header className="bar">
        <div>
          <h1>Ops Center GraphRAG</h1>
          <p className="sub">
            {user?.full_name || username} · {user?.role || "ops"}
          </p>
        </div>
        <button type="button" className="ghost" onClick={logout}>
          Log out
        </button>
      </header>

      <div className="chat">
        {messages.length === 0 && (
          <p className="hint">
            Try: ownership contacts, dependency impact, SME report fields, or active change requests.
          </p>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`bubble ${msg.role}`}>
            <pre>{msg.text}</pre>
            {msg.meta && <span className="meta">{msg.meta}</span>}
          </div>
        ))}
      </div>

      <form className="composer card" onSubmit={ask}>
        <label>
          Mode
          <select value={mode} onChange={(e) => setMode(e.target.value)}>
            <option value="auto">Auto (LangGraph route)</option>
            <option value="graph">Graph only</option>
            <option value="vector">Vector only</option>
          </select>
        </label>
        <label>
          Question
          <textarea
            rows={3}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Describe the incident or ask about dependencies…"
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={loading}>
          {loading ? "Thinking…" : "Ask"}
        </button>
      </form>
    </div>
  );
}
