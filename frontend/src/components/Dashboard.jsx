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
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header & Refresh */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
            Knowledge Gap & System Analytics
          </h2>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Real-time insights into enterprise query performance, unanswered questions, and time savings.
          </p>
        </div>
        <button
          onClick={fetchData}
          disabled={loading}
          className="inline-flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium rounded-lg text-slate-700 dark:text-slate-200 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700/50 shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50"
        >
          <svg
            className={`w-4 h-4 text-slate-500 ${loading ? 'animate-spin' : ''}`}
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
          {loading ? 'Refreshing...' : 'Refresh Data'}
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800/60 text-red-700 dark:text-red-300 text-sm">
          {error}
        </div>
      )}

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-5">
        {/* Total Questions */}
        <div className="bg-white dark:bg-slate-800/80 rounded-xl p-5 border border-slate-200/80 dark:border-slate-700/60 shadow-sm">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
            Total Queries
          </span>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-slate-900 dark:text-white">
              {stats.total_questions ?? 0}
            </span>
          </div>
          <div className="mt-2 text-xs text-slate-500 dark:text-slate-400">
            Across all enterprise roles
          </div>
        </div>

        {/* Answered */}
        <div className="bg-white dark:bg-slate-800/80 rounded-xl p-5 border border-slate-200/80 dark:border-slate-700/60 shadow-sm">
          <span className="text-xs font-semibold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">
            Answered
          </span>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-emerald-600 dark:text-emerald-400">
              {stats.answered ?? 0}
            </span>
          </div>
          <div className="mt-2 text-xs text-slate-500 dark:text-slate-400">
            {stats.total_questions > 0
              ? `${Math.round(((stats.answered || 0) / stats.total_questions) * 100)}% resolution rate`
              : 'Verified with citations'}
          </div>
        </div>

        {/* Unanswered */}
        <div className="bg-white dark:bg-slate-800/80 rounded-xl p-5 border border-slate-200/80 dark:border-slate-700/60 shadow-sm">
          <span className="text-xs font-semibold uppercase tracking-wider text-amber-600 dark:text-amber-400">
            Unanswered Gaps
          </span>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-amber-600 dark:text-amber-400">
              {stats.unanswered ?? 0}
            </span>
          </div>
          <div className="mt-2 text-xs text-slate-500 dark:text-slate-400">
            Refused or low confidence
          </div>
        </div>

        {/* Conflicts Flagged */}
        <div className="bg-white dark:bg-slate-800/80 rounded-xl p-5 border border-slate-200/80 dark:border-slate-700/60 shadow-sm">
          <span className="text-xs font-semibold uppercase tracking-wider text-rose-600 dark:text-rose-400">
            Conflicts Flagged
          </span>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-rose-600 dark:text-rose-400">
              {stats.conflicts_flagged ?? 0}
            </span>
          </div>
          <div className="mt-2 text-xs text-slate-500 dark:text-slate-400">
            Contradictions & staleness
          </div>
        </div>

        {/* Minutes Saved */}
        <div className="bg-white dark:bg-slate-800/80 rounded-xl p-5 border border-slate-200/80 dark:border-slate-700/60 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-indigo-600 dark:text-indigo-400">
              Time Saved
            </span>
            <span className="text-[10px] font-medium px-1.5 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800">
              Estimate
            </span>
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-indigo-600 dark:text-indigo-400">
              {stats.total_minutes_saved != null ? Number(stats.total_minutes_saved).toFixed(1) : '0.0'}
              <span className="text-base font-semibold text-slate-500 dark:text-slate-400 ml-1">m</span>
            </span>
          </div>
          <div className="mt-2 text-xs text-slate-500 dark:text-slate-400">
            Estimated search minutes saved
          </div>
        </div>
      </div>

      {/* Role Breakdown Badge Row */}
      {stats.by_role && Object.keys(stats.by_role).length > 0 && (
        <div className="flex flex-wrap items-center gap-2 p-3 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-700/40 text-xs text-slate-600 dark:text-slate-300">
          <span className="font-semibold text-slate-700 dark:text-slate-200 mr-2">Query Distribution by Role:</span>
          {Object.entries(stats.by_role).map(([role, count]) => (
            <span
              key={role}
              className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full font-medium bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 text-slate-800 dark:text-slate-200 shadow-2xs"
            >
              <span className="capitalize">{role}</span>:
              <span className="font-bold text-indigo-600 dark:text-indigo-400">{count}</span>
            </span>
          ))}
        </div>
      )}

      {/* Knowledge Gap Dashboard & Chart */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
            Knowledge Gaps & Unanswered Topics
          </h3>
          <span className="text-xs text-slate-500 dark:text-slate-400">
            Clustered by question similarity (Jaccard &ge; 0.6)
          </span>
        </div>

        {gaps.length === 0 ? (
          <div className="text-center py-16 px-4 rounded-xl bg-white dark:bg-slate-800/40 border border-dashed border-slate-300 dark:border-slate-700">
            <svg
              className="mx-auto h-12 w-12 text-slate-400 dark:text-slate-500"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="1.5"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <h4 className="mt-3 text-sm font-semibold text-slate-900 dark:text-white">No Knowledge Gaps Detected</h4>
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400 max-w-sm mx-auto">
              Knowledge gaps appear here automatically when employees ask questions that receive low confidence or no answers.
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Horizontal Bar Chart (Plain Tailwind Divs) */}
            <div className="bg-white dark:bg-slate-800/80 rounded-xl p-6 border border-slate-200/80 dark:border-slate-700/60 shadow-sm space-y-4">
              <h4 className="text-sm font-semibold text-slate-800 dark:text-slate-200">
                Frequently Asked Gaps (Frequency Distribution)
              </h4>
              <div className="space-y-3 pt-2">
                {gaps.map((gap, idx) => {
                  const widthPercent = Math.max(8, Math.round((gap.asked_count / maxGapCount) * 100));
                  return (
                    <div key={idx} className="space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-medium text-slate-700 dark:text-slate-300 truncate max-w-md">
                          {gap.question}
                        </span>
                        <span className="font-semibold text-indigo-600 dark:text-indigo-400 ml-2 shrink-0">
                          {gap.asked_count} {gap.asked_count === 1 ? 'time' : 'times'}
                        </span>
                      </div>
                      <div className="w-full bg-slate-100 dark:bg-slate-700/60 rounded-full h-3 overflow-hidden">
                        <div
                          className="bg-indigo-600 dark:bg-indigo-500 h-3 rounded-full transition-all duration-500 ease-out"
                          style={{ width: `${widthPercent}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Gap Items Table */}
            <div className="bg-white dark:bg-slate-800/80 rounded-xl border border-slate-200/80 dark:border-slate-700/60 shadow-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-700/60 text-left text-xs">
                  <thead className="bg-slate-50 dark:bg-slate-900/40 text-slate-500 dark:text-slate-400 font-semibold uppercase tracking-wider">
                    <tr>
                      <th className="py-3.5 px-4 sm:px-6">Question / Gap Description</th>
                      <th className="py-3.5 px-4 text-center">Frequency</th>
                      <th className="py-3.5 px-4">Last Asked</th>
                      <th className="py-3.5 px-4 sm:px-6">Missing Information / Reason</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 dark:divide-slate-700/40 text-slate-700 dark:text-slate-200">
                    {gaps.map((gap, idx) => (
                      <tr key={idx} className="hover:bg-slate-50/70 dark:hover:bg-slate-700/30 transition-colors">
                        <td className="py-3.5 px-4 sm:px-6 font-medium text-slate-900 dark:text-white max-w-sm sm:max-w-md break-words">
                          {gap.question}
                        </td>
                        <td className="py-3.5 px-4 text-center">
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
                            {gap.asked_count}
                          </span>
                        </td>
                        <td className="py-3.5 px-4 text-slate-500 dark:text-slate-400 font-mono">
                          {gap.last_asked}
                        </td>
                        <td className="py-3.5 px-4 sm:px-6 text-slate-600 dark:text-slate-300">
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
