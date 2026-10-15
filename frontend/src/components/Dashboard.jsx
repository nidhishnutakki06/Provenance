import React, { useState, useEffect, useCallback } from 'react';
import * as api from '../api';

export default function Dashboard() {
  const [stats, setStats] = useState({
    total_questions: 0,
    answered: 0,
    unanswered: 0,
    total_minutes_saved: 0.0,
    conflicts_flagged: 0,
    by_role: {},
  });
  const [gaps, setGaps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      let statsData = null;
      let gapsData = null;

      if (api && typeof api.getStats === 'function') {
        statsData = await api.getStats();
      } else {
        const res = await fetch('http://localhost:8000/stats');
        statsData = await res.json();
      }

      if (api && typeof api.getGaps === 'function') {
        gapsData = await api.getGaps();
      } else {
        const res = await fetch('http://localhost:8000/gaps');
        gapsData = await res.json();
      }

      setStats(statsData || {});
      setGaps(Array.isArray(gapsData) ? gapsData : []);
    } catch (err) {
      console.error('Failed to load dashboard metrics:', err);
      setError('Unable to load metrics from the server. Ensure the backend is running.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Max count for proportional bar chart widths
  const maxGapCount = gaps.length > 0 ? Math.max(...gaps.map((g) => g.asked_count || 1)) : 1;

  return (
    <div className="max-w-[1200px] mx-auto space-y-8">
      {/* Header & Refresh */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-[var(--border)]">
        <div>
          <h2 className="text-2xl sm:text-3xl font-display font-semibold text-[var(--text)] tracking-tight">
            Knowledge Gaps & Analytics
          </h2>
          <p className="mt-1 text-xs sm:text-sm text-[var(--text-muted)]">
            Continuous enterprise query insights, unanswered topic discovery, and estimated literature search savings.
          </p>
        </div>
        <button
          onClick={fetchData}
          disabled={loading}
          className="inline-flex items-center justify-center gap-2 px-4 py-2.5 text-xs sm:text-sm font-semibold rounded-xl text-[var(--text)] bg-[var(--surface)] border border-[var(--border)] hover:bg-[var(--surface-2)] shadow-soft-sm transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)] disabled:opacity-50 self-start sm:self-auto"
        >
          <svg
            className={`w-4 h-4 text-[var(--text-muted)] ${loading ? 'animate-spin' : ''}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
          <span>{loading ? 'Refreshing...' : 'Refresh Data'}</span>
        </button>
      </div>

      {error && (
        <div
          role="alert"
          className="p-4 rounded-xl bg-[#FBEEEC] dark:bg-[#381310] border border-[#C4483E]/40 text-[#C4483E] dark:text-[#F79B95] text-xs sm:text-sm shadow-soft-sm"
        >
          {error}
        </div>
      )}

      {/* 5 KPI Metric Cards with Large Playfair Numbers */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 sm:gap-5">
        {/* Total Questions */}
        <div className="bg-[var(--surface)] rounded-2xl p-5 border border-[var(--border)] shadow-soft-sm space-y-2">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-[var(--text-muted)]">
            Total Queries
          </span>
          <div className="text-3xl sm:text-4xl font-display font-semibold text-[var(--text)]">
            {stats.total_questions ?? 0}
          </div>
          <div className="text-[11px] text-[var(--text-muted)]">
            Across all enterprise roles
          </div>
        </div>

        {/* Answered */}
        <div className="bg-[var(--surface)] rounded-2xl p-5 border border-[var(--border)] shadow-soft-sm space-y-2">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-[#1A634E] dark:text-[#7FE4C4]">
            Verified Answers
          </span>
          <div className="text-3xl sm:text-4xl font-display font-semibold text-[#2E8B6E]">
            {stats.answered ?? 0}
          </div>
          <div className="text-[11px] text-[var(--text-muted)]">
            {stats.total_questions > 0
              ? `${Math.round(((stats.answered || 0) / stats.total_questions) * 100)}% resolution rate`
              : 'Backed by citations'}
          </div>
        </div>

        {/* Unanswered Gaps */}
        <div className="bg-[var(--surface)] rounded-2xl p-5 border border-[var(--border)] shadow-soft-sm space-y-2">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-[#875608] dark:text-[#F6C774]">
            Knowledge Gaps
          </span>
          <div className="text-3xl sm:text-4xl font-display font-semibold text-[#C98A1B]">
            {stats.unanswered ?? 0}
          </div>
          <div className="text-[11px] text-[var(--text-muted)]">
            Refused or weak evidence
          </div>
        </div>

        {/* Conflicts Flagged */}
        <div className="bg-[var(--surface)] rounded-2xl p-5 border border-[var(--border)] shadow-soft-sm space-y-2">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-[#9B2B23] dark:text-[#F79B95]">
            Conflicts Flagged
          </span>
          <div className="text-3xl sm:text-4xl font-display font-semibold text-[#C4483E]">
            {stats.conflicts_flagged ?? 0}
          </div>
          <div className="text-[11px] text-[var(--text-muted)]">
            Contradictions & staleness
          </div>
        </div>

        {/* Minutes Saved */}
        <div className="bg-[var(--surface)] rounded-2xl p-5 border border-[var(--border)] shadow-soft-sm space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-[var(--accent)]">
              Time Saved
            </span>
            <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-[var(--accent-soft)] text-[var(--accent)] border border-[var(--accent)]/30">
              EST
            </span>
          </div>
          <div className="text-3xl sm:text-4xl font-display font-semibold text-[var(--accent)] flex items-baseline">
            {stats.total_minutes_saved != null ? Number(stats.total_minutes_saved).toFixed(1) : '0.0'}
            <span className="text-base font-normal text-[var(--text-muted)] ml-1">m</span>
          </div>
          <div className="text-[11px] text-[var(--text-muted)]">
            Estimated literature search savings
          </div>
        </div>
      </div>

      {/* Role Breakdown Badge Row */}
      {stats.by_role && Object.keys(stats.by_role).length > 0 && (
        <div className="flex flex-wrap items-center gap-2.5 p-3.5 rounded-xl bg-[var(--surface)] border border-[var(--border)] text-xs text-[var(--text)] shadow-soft-sm">
          <span className="font-semibold text-[var(--text-muted)] mr-1">Query Distribution by Role:</span>
          {Object.entries(stats.by_role).map(([rName, count]) => (
            <span
              key={rName}
              className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full font-mono font-medium bg-[var(--surface-2)] border border-[var(--border)] text-[var(--text)]"
            >
              <span className="capitalize">{rName}</span>:
              <strong className="text-[var(--accent)]">{count}</strong>
            </span>
          ))}
        </div>
      )}

      {/* Knowledge Gap Dashboard & Horizontal Bar Chart */}
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1">
          <h3 className="text-lg sm:text-xl font-display font-semibold text-[var(--text)] tracking-tight">
            Knowledge Gaps & Unanswered Topics
          </h3>
          <span className="text-xs font-mono text-[var(--text-muted)]">
            Clustered by question similarity (Jaccard &ge; 0.6)
          </span>
        </div>

        {gaps.length === 0 ? (
          <div className="text-center py-16 px-4 rounded-2xl bg-[var(--surface)] border border-dashed border-[var(--border)] space-y-3">
            <div className="w-12 h-12 mx-auto rounded-2xl bg-[var(--surface-2)] flex items-center justify-center text-[var(--text-muted)]">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h4 className="text-base font-display font-semibold text-[var(--text)]">
              No Knowledge Gaps Detected
            </h4>
            <p className="text-xs text-[var(--text-muted)] max-w-sm mx-auto">
              Knowledge gaps appear here automatically when employees ask questions that receive low confidence or no answers.
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Horizontal Bar Chart (Plain Tailwind Divs in Accent Color) */}
            <div className="bg-[var(--surface)] rounded-2xl p-6 border border-[var(--border)] shadow-soft-sm space-y-4">
              <h4 className="text-sm font-semibold text-[var(--text)] tracking-tight">
                Frequently Asked Gaps (Frequency Distribution)
              </h4>
              <div className="space-y-3 pt-2">
                {gaps.map((gap, idx) => {
                  const widthPercent = Math.max(10, Math.round((gap.asked_count / maxGapCount) * 100));
                  return (
                    <div key={idx} className="space-y-1.5">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-medium text-[var(--text)] truncate max-w-md sm:max-w-xl">
                          {gap.question}
                        </span>
                        <span className="font-mono font-semibold text-[var(--accent)] ml-2 shrink-0">
                          {gap.asked_count} {gap.asked_count === 1 ? 'time' : 'times'}
                        </span>
                      </div>
                      <div className="w-full bg-[var(--surface-2)] rounded-full h-2.5 overflow-hidden border border-[var(--border)]">
                        <div
                          className="bg-[var(--accent)] h-full rounded-full transition-all duration-500 ease-out"
                          style={{ width: `${widthPercent}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Gap Items Table */}
            <div className="bg-[var(--surface)] rounded-2xl border border-[var(--border)] shadow-soft-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-[var(--border)] text-left text-xs">
                  <thead className="bg-[var(--surface-2)] text-[var(--text-muted)] font-semibold uppercase tracking-wider">
                    <tr>
                      <th className="py-3.5 px-4 sm:px-6">Question / Gap Description</th>
                      <th className="py-3.5 px-4 text-center">Frequency</th>
                      <th className="py-3.5 px-4">Last Asked</th>
                      <th className="py-3.5 px-4 sm:px-6">Missing Information / Reason</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[var(--border)] text-[var(--text)]">
                    {gaps.map((gap, idx) => (
                      <tr key={idx} className="hover:bg-[var(--surface-2)]/60 transition-colors">
                        <td className="py-3.5 px-4 sm:px-6 font-medium text-[var(--text)] max-w-sm sm:max-w-md break-words">
                          {gap.question}
                        </td>
                        <td className="py-3.5 px-4 text-center">
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-mono font-semibold bg-[var(--accent-soft)] text-[var(--accent)] border border-[var(--accent)]/30">
                            {gap.asked_count}
                          </span>
                        </td>
                        <td className="py-3.5 px-4 text-[var(--text-muted)] font-mono">
                          {gap.last_asked}
                        </td>
                        <td className="py-3.5 px-4 sm:px-6 text-[var(--text-muted)]">
                          {gap.reason || 'No accessible source found'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
