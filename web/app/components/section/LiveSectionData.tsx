"use client";

import { useEffect, useState } from "react";

import { getStoredToken } from "../../lib/authToken";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "";

type Props = {
  sectionKey: string;
};

function endpointForSection(sectionKey: string): string | null {
  if (sectionKey === "club") {
    return "/api/v1/club";
  }
  if (sectionKey === "squad") {
    return "/api/v1/squad";
  }
  if (sectionKey === "league") {
    return "/api/v1/league/table";
  }
  return null;
}

export default function LiveSectionData({ sectionKey }: Props) {
  const [state, setState] = useState<string>("Loading...");

  useEffect(() => {
    const token = getStoredToken();
    if (!token) {
      setState("Login required for live data.");
      return;
    }

    const endpoint = endpointForSection(sectionKey);
    if (!endpoint) {
      setState("");
      return;
    }

    let isCancelled = false;
    fetch(`${API_BASE}${endpoint}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((resp) => resp.json())
      .then((payload) => {
        if (isCancelled) {
          return;
        }
        if (!payload.ok) {
          setState(payload.error?.message ?? "Failed to load section data");
          return;
        }

        if (sectionKey === "club") {
          const data = payload.data;
          setState(`Club: ${data.name} | Money: ${data.money} | Stars: ${data.stars}`);
          return;
        }
        if (sectionKey === "squad") {
          const data = payload.data;
          const avg =
            data.count > 0
              ? (
                  data.players.reduce((sum: number, p: { strength: number }) => sum + Number(p.strength), 0) /
                  data.count
                ).toFixed(2)
              : "0.00";
          setState(`Players: ${data.count} | Avg strength: ${avg}`);
          return;
        }
        if (sectionKey === "league") {
          const data = payload.data;
          const leader = data.rows?.[0];
          if (leader) {
            setState(`Season ${data.seasonId} leader clubId=${leader.clubId} points=${leader.points}`);
          } else {
            setState(`Season ${data.seasonId} has no published rows yet.`);
          }
          return;
        }
      })
      .catch(() => {
        if (!isCancelled) {
          setState("Network error loading section data");
        }
      });

    return () => {
      isCancelled = true;
    };
  }, [sectionKey]);

  if (!state) {
    return null;
  }

  return <p className="status">{state}</p>;
}
