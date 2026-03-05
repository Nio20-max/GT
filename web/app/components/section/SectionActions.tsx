"use client";

import { useState } from "react";

import { getStoredToken } from "../../lib/authToken";
import { apiGet, apiPost, apiPut } from "../../lib/apiClient";

type Props = {
  sectionKey: string;
};

export default function SectionActions({ sectionKey }: Props) {
  const [output, setOutput] = useState("");

  async function runTrainingAction() {
    const token = getStoredToken();
    if (!token) {
      setOutput("Login required.");
      return;
    }
    const result = await apiPost<{ updated: boolean }>(
      "/api/v1/training/team",
      { style: "balanced", intensity: 55 },
      token
    );
    setOutput(result.ok ? "Training plan updated." : result.error?.message ?? "Training update failed");
  }

  async function runLineupAction() {
    const token = getStoredToken();
    if (!token) {
      setOutput("Login required.");
      return;
    }
    const fixtures = await apiGet<{ fixtures: Array<{ fixtureId: number }> }>("/api/v1/lineup/upcoming", token);
    if (!fixtures.ok || fixtures.data.fixtures.length === 0) {
      setOutput("No fixtures available.");
      return;
    }
    const fixtureId = fixtures.data.fixtures[0].fixtureId;
    const put = await apiPut<{ queued: boolean }>(
      `/api/v1/lineup/upcoming/${fixtureId}`,
      { formation: "4-3-3", playerIds: [] },
      token
    );
    if (put.ok) {
      setOutput(put.data.queued ? "Lineup queued (fixture locked)." : "Lineup updated for upcoming fixture.");
      return;
    }
    setOutput(put.error?.message ?? "Lineup update failed");
  }

  async function runMarketAction() {
    const token = getStoredToken();
    if (!token) {
      setOutput("Login required.");
      return;
    }
    const auctions = await apiGet<{ auctions: Array<{ auctionId: string; currentBid: number }> }>(
      "/api/v1/transfer/auctions",
      token
    );
    if (!auctions.ok || auctions.data.auctions.length === 0) {
      setOutput("No auctions available.");
      return;
    }
    const first = auctions.data.auctions[0];
    const bid = await apiPost<{ placed: boolean }>(
      `/api/v1/transfer/auctions/${first.auctionId}/bid`,
      { amount: Number(first.currentBid) + 1000 },
      token
    );
    setOutput(bid.ok ? "Bid placed on first auction." : bid.error?.message ?? "Bid failed");
  }

  async function runShopAction() {
    const token = getStoredToken();
    if (!token) {
      setOutput("Login required.");
      return;
    }
    const key = `web-${Date.now()}`;
    const grant = await apiPost<{ granted: boolean }>(
      "/api/v1/shop/offers/1/grant",
      {},
      token,
      { "Idempotency-Key": key }
    );
    setOutput(grant.ok ? "Shop grant credited." : grant.error?.message ?? "Shop grant failed");
  }

  return (
    <div className="feature-card">
      <h3>Quick Action</h3>
      {sectionKey === "training" ? <button onClick={runTrainingAction}>Apply Training Plan</button> : null}
      {sectionKey === "lineup" ? <button onClick={runLineupAction}>Set Upcoming Lineup</button> : null}
      {sectionKey === "market" ? <button onClick={runMarketAction}>Place Market Bid</button> : null}
      {sectionKey === "club" ? <button onClick={runShopAction}>Claim Shop Grant</button> : null}
      {output ? <p className="status">{output}</p> : null}
    </div>
  );
}
