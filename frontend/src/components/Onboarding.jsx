import React, { useState, useEffect } from 'react';
import { useRole } from '../context/RoleContext';
import * as api from '../api';

const JOB_ROLES = [
  { id: 'QA', label: 'Quality Assurance (QA)' },
  { id: 'Production', label: 'Manufacturing & Production' },
  { id: 'Regulatory', label: 'Regulatory Affairs' },
];

export default function Onboarding() {
  const { role } = useRole();
  const [jobRole, setJobRole] = useState('QA');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    let active = true;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const res = await api.getOnboarding(jobRole, role);
        if (active) {
          setData(res);
        }
      } catch (err) {
        if (active) {
          console.error('Failed to fetch onboarding path:', err);
          setError('Failed to load onboarding reading path. Please ensure backend is reachable.');
        }
      } finally {
        if (active) setLoading(false);
      }
    }
    load();
    return () => {
      active = false;
    };
  }, [jobRole, role]);

  const daysObj = data?.days || {};
  const dayKeys = Object.keys(daysObj);

  // Calculate total reading minutes across all items
  let totalMinutes = 0;
  dayKeys.forEach((k) => {
    const items = daysObj[k] || [];
    items.forEach((it) => {
      totalMinutes += it.est_minutes || it.est_reading_minutes || 5;
    });
  });

  return (
    <div className="max-w-[860px] mx-auto space-y-6">
      {/* Curriculum Header Card */}
      <div className="bg-[var(--surface)] rounded-2xl p-6 sm:p-7 shadow-soft-sm border border-[var(--border)] space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h2 className="text-xl sm:text-2xl font-display font-semibold text-[var(--text)] tracking-tight">
              Curated Onboarding Path
            </h2>
            <p className="text-xs sm:text-sm text-[var(--text-muted)] mt-1 leading-relaxed">
              Tailored 5-day reading sequence filtered strictly for your security clearance (
              <strong className="text-[var(--text)] uppercase font-mono">{role}</strong>). Restricted documents are excluded.
            </p>
          </div>

          {totalMinutes > 0 && (
            <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[var(--accent-soft)] text-[var(--accent)] font-medium text-xs border border-[var(--accent)]/20 shrink-0 self-start sm:self-auto">
              <span>⏱ Total Reading Time:</span>
              <span className="font-bold">{totalMinutes} mins</span>
            </div>
          )}
        </div>

        {/* Job Role Pills */}
        <div className="flex flex-wrap gap-2 pt-3 border-t border-[var(--border)]">
          {JOB_ROLES.map((jr) => (
            <button
              key={jr.id}
              onClick={() => setJobRole(jr.id)}
              className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all duration-150 focus-visible:ring-2 focus-visible:ring-[var(--accent)] ${
                jobRole === jr.id
                  ? 'bg-[var(--accent)] text-white shadow-soft-sm'
                  : 'bg-[var(--surface-2)] hover:bg-[var(--accent-soft)] text-[var(--text)] border border-[var(--border)]'
              }`}
            >
              {jr.label}
            </button>
          ))}
        </div>
      </div>

      {/* Loading Skeleton */}
      {loading && (
        <div className="py-12 text-center text-[var(--text-muted)] text-sm flex items-center justify-center gap-2">
          <svg className="animate-spin h-4 w-4 text-[var(--accent)]" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
          </svg>
          <span>Curating role-based curriculum for {jobRole}...</span>
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
      {!loading && !error && dayKeys.length === 0 && (
        <div className="text-center py-16 bg-[var(--surface)] rounded-2xl border border-dashed border-[var(--border)] p-8 space-y-3">
          <div className="w-12 h-12 mx-auto rounded-2xl bg-[var(--surface-2)] flex items-center justify-center text-[var(--text-muted)]">
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <h3 className="text-base font-display font-semibold text-[var(--text)]">
            No Reading Materials Found
          </h3>
          <p className="text-xs text-[var(--text-muted)] max-w-md mx-auto">
            No onboarding curriculum is available for this clearance level and role combination.
          </p>
        </div>
      )}

      {/* 5-Day Timeline */}
      {!loading && !error && dayKeys.length > 0 && (
        <div className="space-y-5">
          {dayKeys.map((dayKey) => {
            const items = daysObj[dayKey] || [];
            if (items.length === 0) return null;

            return (
              <div
                key={dayKey}
                className="bg-[var(--surface)] rounded-2xl p-6 shadow-soft-sm border border-[var(--border)] space-y-4"
              >
                {/* Day Header with Playfair Display */}
                <div className="flex items-center justify-between border-b border-[var(--border)] pb-3">
                  <div className="flex items-center gap-2.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-[var(--accent)]" />
                    <h3 className="text-base sm:text-lg font-display font-semibold tracking-tight text-[var(--text)]">
                      {dayKey}
                    </h3>
                  </div>
                  <span className="text-xs font-mono text-[var(--text-muted)]">
                    {items.length} document{items.length > 1 ? 's' : ''}
                  </span>
                </div>

                {/* Day Reading Items */}
                <div className="space-y-3">
                  {items.map((item, idx) => (
                    <div
                      key={idx}
                      className="p-4 rounded-xl border border-[var(--border)] bg-[var(--surface-2)]/60 hover:bg-[var(--surface-2)] transition-all duration-150 space-y-2"
                    >
                      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2">
                        <div className="space-y-1">
                          <div className="flex flex-wrap items-center gap-2">
                            <span className="px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-[var(--surface)] text-[var(--text-muted)] border border-[var(--border)]">
                              #{item.order || idx + 1}
                            </span>
                            <span className="text-xs font-mono font-bold text-[var(--accent)]">
                              {item.doc_id}
                            </span>
                            <span className="text-sm font-semibold text-[var(--text)]">
                              {item.title}
                            </span>
                          </div>
                          {item.why && (
                            <p className="text-xs text-[var(--text-muted)] leading-relaxed pl-1 pt-0.5">
                              {item.why}
                            </p>
                          )}
                        </div>

                        <span className="inline-flex items-center self-start px-2.5 py-0.5 rounded-full text-xs font-mono font-medium bg-[#FCF5E8] text-[#875608] border border-[#C98A1B]/30 dark:bg-[#382506] dark:text-[#F6C774] shrink-0">
                          ⏱ ~{item.est_minutes || item.est_reading_minutes || 5} mins
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
