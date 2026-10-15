import React, { useState, useEffect } from 'react';
import { useRole } from '../context/RoleContext';
import * as api from '../api';

const TOPIC_SUGGESTIONS = ['deviation', 'capa', 'cold-chain', 'audit'];

export default function Experts() {
  const { role } = useRole();
  const [topic, setTopic] = useState('deviation');
  const [expertsList, setExpertsList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchExperts = async (t) => {
    const currentTopic = (t || topic).trim();
    if (!currentTopic) return;

    setLoading(true);
    setError(null);
    try {
      const data = await api.getExperts(currentTopic, role);
      setExpertsList(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Failed to fetch experts:', err);
      setError('Unable to find experts for this topic. Ensure backend is reachable.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExperts(topic);
  }, [topic, role]);

  return (
    <div className="max-w-[860px] mx-auto space-y-6">
      {/* Search Header and Suggestion Chips */}
      <div className="bg-[var(--surface)] rounded-2xl p-6 sm:p-7 shadow-soft-sm border border-[var(--border)] space-y-4">
        <div>
          <label
            htmlFor="expert-topic-input"
            className="block text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)] mb-2"
          >
            Find Subject Matter Experts by Domain Topic
          </label>
          <div className="relative flex items-center rounded-xl bg-[var(--surface-2)] border border-[var(--border)] focus-within:ring-2 focus-within:ring-[var(--accent)] focus-within:border-transparent transition-all shadow-soft-sm">
            <input
              id="expert-topic-input"
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') fetchExperts(topic);
              }}
              placeholder="e.g. deviation, capa, cold-chain..."
              className="w-full bg-transparent pl-4 pr-28 py-3 text-sm text-[var(--text)] placeholder:text-[var(--text-muted)]/60 focus:outline-none"
            />
            <button
              type="button"
              onClick={() => fetchExperts(topic)}
              disabled={loading || !topic.trim()}
              className="absolute right-2 px-4 py-1.5 rounded-lg bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white text-xs font-semibold transition-all duration-150 focus-visible:ring-2 focus-visible:ring-[var(--accent)]"
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </div>

        {/* Suggestion Chips */}
        <div className="flex flex-wrap items-center gap-2 pt-1">
          <span className="text-[11px] font-semibold text-[var(--text-muted)] uppercase tracking-wider">
            Topics:
          </span>
          {TOPIC_SUGGESTIONS.map((sug) => {
            const isActive = topic.toLowerCase() === sug.toLowerCase();
            return (
              <button
                key={sug}
                type="button"
                onClick={() => {
                  setTopic(sug);
                  fetchExperts(sug);
                }}
                className={`px-3 py-1 rounded-xl text-xs font-medium transition-all duration-150 focus-visible:ring-2 focus-visible:ring-[var(--accent)] ${
                  isActive
                    ? 'bg-[var(--accent)] text-white font-semibold shadow-soft-sm'
                    : 'bg-[var(--surface-2)] text-[var(--text)] hover:bg-[var(--accent-soft)] hover:text-[var(--accent)] border border-[var(--border)]'
                }`}
              >
                #{sug}
              </button>
            );
          })}
        </div>
      </div>

      {/* Loading Skeleton */}
      {loading && (
        <div className="py-12 text-center text-[var(--text-muted)] text-sm flex items-center justify-center gap-2">
          <svg className="animate-spin h-4 w-4 text-[var(--accent)]" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
          </svg>
          <span>Ranking experts based on verified document provenance...</span>
        </div>
      )}

      {/* Error state */}
      {error && !loading && (
        <div
          role="alert"
          className="p-4 rounded-xl border border-[#C4483E]/40 bg-[#FBEEEC] dark:bg-[#381310] text-[#C4483E] dark:text-[#F79B95] text-xs sm:text-sm shadow-soft-sm"
        >
          {error}
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && expertsList.length === 0 && (
        <div className="text-center py-16 bg-[var(--surface)] rounded-2xl border border-dashed border-[var(--border)] p-8 space-y-3">
          <div className="w-12 h-12 mx-auto rounded-2xl bg-[var(--surface-2)] flex items-center justify-center text-[var(--text-muted)]">
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8">
              <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <h3 className="text-base font-display font-semibold text-[var(--text)]">
            No Verified Experts Found
          </h3>
          <p className="text-xs text-[var(--text-muted)] max-w-md mx-auto">
            No subject matter experts have authored or signed approved documentation matching topic "{topic}" within your role clearance ({role}).
          </p>
        </div>
      )}

      {/* Experts Grid */}
      {!loading && !error && expertsList.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {expertsList.map((exp, idx) => (
            <div
              key={idx}
              className="bg-[var(--surface)] rounded-2xl p-6 shadow-soft-sm border border-[var(--border)] flex flex-col justify-between space-y-4 hover:border-[var(--accent)]/40 transition-all duration-200"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-2xl bg-[var(--accent-soft)] border border-[var(--accent)]/30 flex items-center justify-center font-bold text-sm text-[var(--accent)] shrink-0">
                      {exp.name.split(' ').map((n) => n[0]).join('')}
                    </div>
                    <div>
                      <h3 className="text-base sm:text-lg font-display font-semibold text-[var(--text)] tracking-tight">
                        {exp.name}
                      </h3>
                      <p className="text-xs text-[var(--text-muted)]">
                        {exp.role || 'Domain Contributor'}
                      </p>
                    </div>
                  </div>

                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-mono font-semibold bg-[#E6F4EE] text-[#1A634E] border border-[#2E8B6E]/30 dark:bg-[#0D2B22] dark:text-[#7FE4C4] shrink-0">
                    {exp.evidence_count} doc{exp.evidence_count > 1 ? 's' : ''}
                  </span>
                </div>

                {/* Topics */}
                {exp.topics && exp.topics.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {exp.topics.map((tp, tIdx) => (
                      <span
                        key={tIdx}
                        className="px-2 py-0.5 rounded-lg text-[11px] font-mono font-medium bg-[var(--surface-2)] text-[var(--text)] border border-[var(--border)]"
                      >
                        #{tp}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Sample Source Provenance */}
              {exp.sample_source && (
                <div className="pt-3 border-t border-[var(--border)] text-xs text-[var(--text-muted)]">
                  <span className="font-semibold text-[var(--text)]">Authored Source: </span>
                  <span className="italic">{exp.sample_source}</span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
