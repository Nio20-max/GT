"use client";

import { useEffect, useState } from "react";

type EventRow = {
  cursor?: number;
  event?: string;
  timestampUtc?: string;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "";

export default function RealtimeFeed() {
  const [rows, setRows] = useState<EventRow[]>([]);

  useEffect(() => {
    const base = API_BASE || window.location.origin;
    const wsUrl = `${base.replace(/^http/, "ws")}/api/v1/realtime`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      ws.send(JSON.stringify({ action: "subscribe", topics: ["scheduler", "settlements", "notifications"] }));
    };

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (!payload?.ok || !payload?.data) {
          return;
        }
        const data = payload.data;
        if (!data.event || !data.timestampUtc) {
          return;
        }
        setRows((prev) => [data as EventRow, ...prev].slice(0, 8));
      } catch {
        // Ignore non-JSON messages.
      }
    };

    return () => {
      ws.close();
    };
  }, []);

  return (
    <section className="feature-card">
      <h3>Realtime Feed</h3>
      {rows.length === 0 ? <p>No live events yet.</p> : null}
      <ul className="bullet-list">
        {rows.map((row, idx) => (
          <li key={`${row.cursor ?? idx}`}>{`${row.event} @ ${row.timestampUtc}`}</li>
        ))}
      </ul>
    </section>
  );
}
