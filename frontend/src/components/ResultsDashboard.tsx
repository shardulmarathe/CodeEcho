"use client";

import { useState } from "react";
import type { SessionResult, TabId } from "@/lib/types";
import { Timeline } from "./Timeline";
import { OverviewTab, AnalyticsTab, HistoryTab } from "./ResultsTabs";
import { TranscriptView } from "./TranscriptView";

interface ResultsDashboardProps {
  session: SessionResult;
  onNewSession: () => void;
}

const TABS: { id: TabId; label: string }[] = [
  { id: "overview", label: "Overview" },
  { id: "timeline", label: "Timeline" },
  { id: "analytics", label: "Analytics" },
  { id: "history", label: "History" },
];

export function ResultsDashboard({ session, onNewSession }: ResultsDashboardProps) {
  const [activeTab, setActiveTab] = useState<TabId>("overview");
  const fillerIndices = new Set(session.fillers.map((f) => f.index));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <p className="eyebrow">delivery analysis</p>
          <h2 className="font-display text-lg font-bold mt-1">
            {session.metrics.total_fillers} filler
            {session.metrics.total_fillers === 1 ? "" : "s"} ·{" "}
            {session.metrics.words_per_minute} wpm
          </h2>
        </div>
        <button onClick={onNewSession} className="text-xs mono text-muted hover:text-echo">
          start over
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 flex-wrap">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 text-sm font-medium transition-all ${
              activeTab === tab.id ? "tab-active" : "tab-inactive"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {activeTab === "overview" && (
        <>
          <OverviewTab metrics={session.metrics} />
          <TranscriptView
            words={session.words}
            fillerIndices={fillerIndices}
            fillers={session.fillers}
            pauses={session.pauses}
          />
        </>
      )}
      {activeTab === "timeline" && (
        <>
          <Timeline
            durationSec={session.metrics.duration_sec}
            fillers={session.fillers}
          />
          <TranscriptView
            words={session.words}
            fillerIndices={fillerIndices}
            fillers={session.fillers}
            pauses={session.pauses}
          />
        </>
      )}
      {activeTab === "analytics" && <AnalyticsTab metrics={session.metrics} />}
      {activeTab === "history" && <HistoryTab />}
    </div>
  );
}
