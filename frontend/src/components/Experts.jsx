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
      console.error("Failed to fetch experts:", err);
      setError("Unable to find experts for this topic. Ensure the backend is reachable.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExperts(topic);
  }, [topic, role]);

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
      {/* Search Header and Suggestion Chips */}
      <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 shadow-sm border border-slate-200 dark:border-slate-800 space-y-4">
        <div>
          <label htmlFor="expert-topic-input" className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-2">
            Find Domain Experts by Topic
          </label>
          <div className="flex gap-2">
            <input
              id="expert-topic-input"
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g. deviation, capa, cold-chain..."
              className="flex-1 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-4 py-3 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <button
              onClick={() => fetchExperts(topic)}
              disabled={loading || !topic.trim()}
              className="px-5 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-sm transition"
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </div>

        {/* Suggestion Chips */}
        <div className="flex flex-wrap items-center gap-2 pt-1">
          <span className="text-xs text-slate-400">Suggestions:</span>
          {TOPIC_SUGGESTIONS.map((sug) => (
            <button
              key={sug}
              onClick={() => {
                setTopic(sug);
                fetchExperts(sug);
              }}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition ${
                topic.toLowerCase() === sug.toLowerCase()
                  ? 'bg-indigo-100 text-indigo-800 dark:bg-indigo-950 dark:text-indigo-200 font-semibold border border-indigo-300 dark:border-indigo-700'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300'
              }`}
            >
              #{sug}
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
          <span>Ranking experts based on verified document provenance...</span>
        </div>
      )}

      {/* Error state */}
      {error && !loading && (
        <div className="p-4 rounded-xl border border-rose-300 bg-rose-50 text-rose-800 dark:bg-rose-950/40 text-sm">
          {error}
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && expertsList.length === 0 && (
        <div className="text-center py-16 bg-white dark:bg-slate-900 rounded-2xl border border-dashed border-slate-300 dark:border-slate-800 p-8 space-y-3">
          <div className="w-12 h-12 mx-auto rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-400 text-xl">
            👤
          </div>
          <h3 className="text-base font-semibold text-slate-900 dark:text-white">
            No Verified Experts Found
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 max-w-md mx-auto">
            No subject matter experts have authored or signed approved documentation matching topic "{topic}" within your role clearance ({role}).
          </p>
        </div>
      )}

      {/* Expert Cards Grid */}
      {!loading && !error && expertsList.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {expertsList.map((exp, idx) => (
            <div
              key={idx}
              className="bg-white dark:bg-slate-900 rounded-2xl p-6 shadow-sm border border-slate-200 dark:border-slate-800 flex flex-col justify-between space-y-4 hover:border-slate-300 dark:hover:border-slate-700 transition"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="w-11 h-11 rounded-full bg-indigo-50 dark:bg-indigo-950/80 border border-indigo-200 dark:border-indigo-800 flex items-center justify-center font-bold text-sm text-indigo-700 dark:text-indigo-300">
                      {exp.name.split(' ').map(n => n[0]).join('')}
                    </div>
                    <div>
                      <h3 className="text-base font-bold text-slate-900 dark:text-white">
                        {exp.name}
                      </h3>
                      <p className="text-xs text-slate-500 dark:text-slate-400">
                        {exp.role || 'Domain Contributor'}
                      </p>
                    </div>
                  </div>

                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                    {exp.evidence_count} doc{exp.evidence_count > 1 ? 's' : ''}
                  </span>
                </div>

                {/* Topics */}
                {exp.topics && exp.topics.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {exp.topics.map((tp, tIdx) => (
                      <span
                        key={tIdx}
                        className="px-2 py-0.5 rounded-md text-[11px] font-medium bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300"
                      >
                        #{tp}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Sample Source Provenance */}
              {exp.sample_source && (
                <div className="pt-3 border-t border-slate-100 dark:border-slate-800 text-xs text-slate-500 dark:text-slate-400">
                  <span className="font-semibold text-slate-600 dark:text-slate-300">Authored Source: </span>
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
