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
          console.error("Failed to fetch onboarding path:", err);
          setError("Failed to load onboarding reading path. Please ensure the backend is running.");
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
  dayKeys.forEach(k => {
    const items = daysObj[k] || [];
    items.forEach(it => {
      totalMinutes += (it.est_minutes || it.est_reading_minutes || 5);
    });
  });

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
      {/* Header and Job Role Selector */}
      <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 shadow-sm border border-slate-200 dark:border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">
              Role-Tailored Onboarding Curriculum
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Curated 5-day reading paths filtered strictly for your security clearance (<strong>{role}</strong>). Superseded and unauthorized documents are automatically excluded.
            </p>
          </div>

          {totalMinutes > 0 && (
            <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300 font-medium text-xs border border-indigo-200 dark:border-indigo-800 self-start sm:self-auto">
              <span>⏱ Total Reading Time:</span>
              <span className="font-bold">{totalMinutes} mins</span>
            </div>
          )}
        </div>

        {/* Job Role Buttons */}
        <div className="flex flex-wrap gap-2 pt-2 border-t border-slate-100 dark:border-slate-800">
          {JOB_ROLES.map((jr) => (
            <button
              key={jr.id}
              onClick={() => setJobRole(jr.id)}
              className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
                jobRole === jr.id
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'bg-slate-100 hover:bg-slate-200 text-slate-700 dark:bg-slate-800 dark:hover:bg-slate-700 dark:text-slate-300'
              }`}
            >
              {jr.label}
            </button>
          ))}
        </div>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="py-12 text-center text-slate-500 text-sm flex items-center justify-center gap-2">
          <svg className="animate-spin h-5 w-5 text-indigo-600" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
          </svg>
          <span>Curating role-based curriculum for {jobRole}...</span>
        </div>
      )}

      {/* Error state */}
      {error && !loading && (
        <div className="p-4 rounded-xl border border-rose-300 bg-rose-50 text-rose-800 dark:bg-rose-950/40 dark:border-rose-900 dark:text-rose-300 text-sm">
          {error}
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && dayKeys.length === 0 && (
        <div className="text-center py-16 bg-white dark:bg-slate-900 rounded-2xl border border-dashed border-slate-300 dark:border-slate-800 p-8 space-y-3">
          <div className="w-12 h-12 mx-auto rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-400">
            📚
          </div>
          <h3 className="text-base font-semibold text-slate-900 dark:text-white">
            No Reading Materials Found
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 max-w-md mx-auto">
            No onboarding curriculum is available for this role and clearance combination. Documents may be restricted or undergoing update.
          </p>
        </div>
      )}

      {/* Timeline Days */}
      {!loading && !error && dayKeys.length > 0 && (
        <div className="space-y-6">
          {dayKeys.map((dayKey) => {
            const items = daysObj[dayKey] || [];
            if (items.length === 0) return null;

            return (
              <div
                key={dayKey}
                className="bg-white dark:bg-slate-900 rounded-2xl p-6 shadow-sm border border-slate-200 dark:border-slate-800 space-y-4"
              >
                <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-indigo-600" />
                    <h3 className="text-sm font-bold uppercase tracking-wider text-slate-900 dark:text-white">
                      {dayKey}
                    </h3>
                  </div>
                  <span className="text-xs text-slate-400 font-medium">
                    {items.length} document{items.length > 1 ? 's' : ''}
                  </span>
                </div>

                <div className="space-y-3">
                  {items.map((item, idx) => (
                    <div
                      key={idx}
                      className="p-4 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-850/40 hover:border-slate-200 dark:hover:border-slate-700 transition space-y-2"
                    >
                      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <span className="px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-slate-200 text-slate-800 dark:bg-slate-800 dark:text-slate-300">
                              #{item.order || idx + 1}
                            </span>
                            <span className="text-xs font-mono font-semibold text-indigo-600 dark:text-indigo-400">
                              {item.doc_id}
                            </span>
                            <span className="text-sm font-semibold text-slate-900 dark:text-white">
                              {item.title}
                            </span>
                          </div>
                          {item.why && (
                            <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed pl-1">
                              {item.why}
                            </p>
                          )}
                        </div>

                        <span className="inline-flex items-center self-start px-2 py-0.5 rounded-full text-xs font-medium bg-amber-50 text-amber-800 border border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800 shrink-0">
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
