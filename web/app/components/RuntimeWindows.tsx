"use client";

import { useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "";

export default function RuntimeWindows() {
  const [text, setText] = useState("Loading runtime windows...");

  useEffect(() => {
    Promise.all([
      fetch(`${API_BASE}/api/v1/runtime/calendar`).then((resp) => resp.json()),
      fetch(`${API_BASE}/api/v1/runtime/locks`).then((resp) => resp.json()),
    ])
      .then(([calendar, locks]) => {
        if (!calendar.ok || !locks.ok) {
          setText("Runtime windows unavailable");
          return;
        }
        const c = calendar.data;
        const l = locks.data;
        setText(
          `League ${c.league.lockUtc}->${c.league.kickoffUtc} UTC | Cup/UCL ${c.cupUcl.lockUtc}->${c.cupUcl.kickoffUtc} UTC | scheduled=${l.scheduled} precomputed=${l.precomputed} published=${l.published}`
        );
      })
      .catch(() => setText("Runtime windows unavailable"));
  }, []);

  return <p className="status">{text}</p>;
}
