BASE_CSS = """
:root {
  color-scheme: dark light;
  --bg: #0f172a;
  --fg: #e2e8f0;
  --card: #1e293b;
  --accent: #38bdf8;
  --ok: #22c55e;
  --warn: #fbbf24;
  --fail: #ef4444;
  font-family: "Segoe UI", "SF Pro Text", Roboto, sans-serif;
}

body {
  background: var(--bg);
  color: var(--fg);
  margin: 0;
  padding: 2rem 3rem 4rem;
}

a {
  color: var(--accent);
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

header {
  margin-bottom: 2rem;
}

.grid {
  display: grid;
  gap: 1.5rem;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

.card {
  background: var(--card);
  border-radius: 16px;
  padding: 1.25rem 1.5rem;
  box-shadow: 0 18px 32px rgba(15, 23, 42, 0.45);
  border: 1px solid rgba(56, 189, 248, 0.08);
}

.card h2 {
  margin-top: 0;
  font-size: 1.15rem;
  letter-spacing: 0.01em;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  border-radius: 9999px;
  padding: 0.15rem 0.75rem;
  font-size: 0.8rem;
  background: rgba(148, 163, 184, 0.2);
}

.badge.ok {
  background: rgba(34, 197, 94, 0.15);
  color: var(--ok);
}

.badge.fail {
  background: rgba(239, 68, 68, 0.18);
  color: var(--fail);
}

.badge.warn {
  background: rgba(251, 191, 36, 0.16);
  color: var(--warn);
}

ul.steplist {
  list-style: none;
  padding-left: 0;
  margin: 0;
}

ul.steplist li {
  margin-bottom: 0.5rem;
}

details {
  background: rgba(30, 41, 59, 0.65);
  border-radius: 14px;
  padding: 0.75rem 1rem;
}

details summary {
  cursor: pointer;
  font-weight: 600;
}

code {
  font-family: "JetBrains Mono", "Fira Code", monospace;
  background: rgba(15, 23, 42, 0.65);
  padding: 0.1rem 0.4rem;
  border-radius: 6px;
  font-size: 0.85rem;
}

.img-wrap {
  margin: 1rem 0;
  background: rgba(15, 23, 42, 0.6);
  border-radius: 18px;
  padding: 1rem;
  text-align: center;
}

.img-wrap img {
  max-width: 100%;
  height: auto;
  border-radius: 12px;
}

.table-compact {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.table-compact th,
.table-compact td {
  text-align: left;
  padding: 0.4rem 0.6rem;
}

.table-compact tr:nth-child(even) {
  background: rgba(148, 163, 184, 0.08);
}
"""
