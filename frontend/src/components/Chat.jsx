import React, { useState, useEffect } from 'react';
import { useRole } from '../context/RoleContext';
import * as api from '../api';
import ConflictBanner from './ConflictBanner';
import ConfidenceBadge from './ConfidenceBadge';
import ExpandedTerms from './ExpandedTerms';
import IDontKnowCard from './IDontKnowCard';
import CitationPanel from './CitationPanel';

const EXAMPLE_QUESTIONS = [
  "What temperature should vaccine batches be stored at?",
  "What is the CAPA timeline for an OOS result?",
  "What recurring deviation did the audit find?",
  "How do I calibrate an HPLC column?",
  "Who knows about deviation handling?"
];

export default function Chat() {
  const { role } = useRole();
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);
  const [activeCitation, setActiveCitation] = useState(null);

  // Clear answer / history or refresh when role changes
  useEffect(() => {
    setActiveCitation(null);
    setError(null);
  }, [role]);

  const handleSubmit = async (qText) => {
    const q = (qText || question).trim();
    if (!q || loading) return;

    setLoading(true);
    setError(null);
    setActiveCitation(null);

    try {
      const resp = await api.ask(q, role);
      setHistory(prev => [...prev, {
        id: Date.now(),
        question: q,
        role,
        response: resp
      }]);
      setQuestion('');
    } catch (err) {
      console.error("Ask query failed:", err);
      setError(err.message || "Failed to reach backend.");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  // Helper to render text with clickable [n] chips
  const renderFormattedAnswer = (text, citations = []) => {
    if (!text) return null;
    const parts = text.split(/(\[\d+\])/g);

    return parts.map((part, index) => {
      const match = part.match(/^\[(\d+)\]$/);
      if (match) {
        const citeNum = parseInt(match[1], 10);
        const cite = citations && citations[citeNum - 1];

        return (
          <button
            key={index}
            type="button"
            onClick={() => setActiveCitation(cite || citations[0])}
            title={cite ? `View citation [${citeNum}]: ${cite.title || cite.doc_id}` : `Citation [${citeNum}]`}
            className="inline-flex items-center px-1.5 py-0.5 mx-0.5 rounded text-xs font-mono font-semibold bg-indigo-100 text-indigo-700 hover:bg-indigo-200 border border-indigo-200 dark:bg-indigo-950/60 dark:text-indigo-300 dark:border-indigo-800 transition-colors cursor-pointer align-baseline"
          >
            [{citeNum}]
          </button>
        );
      }
      return <span key={index}>{part}</span>;
    });
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-6 space-y-6">
      {/* Search Input Box & Example Chips */}
      <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800 p-5 space-y-4">
        <div>
          <label htmlFor="question-input" className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-2">
            Ask Enterprise Knowledge Base ({role.toUpperCase()})
          </label>
          <div className="flex gap-2">
            <input
              id="question-input"
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
              placeholder="e.g. What temperature should vaccine batches be stored at?"
              className="flex-1 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-4 py-3 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400 transition"
            />
            <button
              onClick={() => handleSubmit()}
              disabled={loading || !question.trim()}
              className="px-5 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-medium text-sm flex items-center gap-2 shadow-sm transition-colors"
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-4 w-4 text-white" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                  </svg>
                  <span>Searching...</span>
                </>
              ) : (
                <>
                  <span>Ask</span>
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                  </svg>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Example Questions */}
        <div className="space-y-1.5">
          <div className="text-[11px] font-medium text-slate-400 dark:text-slate-500 uppercase tracking-wider">
            Demo Script Questions:
          </div>
          <div className="flex flex-wrap gap-1.5">
            {EXAMPLE_QUESTIONS.map((ex, i) => (
              <button
                key={i}
                type="button"
                onClick={() => {
                  setQuestion(ex);
                  handleSubmit(ex);
                }}
                disabled={loading}
                className="text-xs px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 text-left transition"
              >
                {ex}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="p-4 rounded-xl border border-rose-300 bg-rose-50 text-rose-800 dark:bg-rose-950/40 dark:border-rose-900 dark:text-rose-300 text-sm flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => setError(null)} className="text-xs underline ml-4">Dismiss</button>
        </div>
      )}

      {/* Conversation History (Newest at Bottom) */}
      <div className="space-y-6">
        {history.length === 0 && !loading && (
          <div className="text-center py-12 text-slate-400 dark:text-slate-500 text-sm">
            Ask a question or select an example above to explore verified enterprise knowledge.
          </div>
        )}

        {history.map((item) => {
          const resp = item.response;
          const isAnswerable = resp && resp.answerable;

          return (
            <div
              key={item.id}
              className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 shadow-sm space-y-4"
            >
              {/* Question bubble */}
              <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-indigo-500" />
                  <span className="text-sm font-semibold text-slate-900 dark:text-white">
                    {item.question}
                  </span>
                </div>
                <span className="text-xs uppercase tracking-wider font-mono text-slate-400">
                  Role: {item.role}
                </span>
              </div>

              {/* If NOT answerable, show ONLY IDontKnowCard with missing_info */}
              {!isAnswerable ? (
                <IDontKnowCard missingInfo={resp?.missing_info} />
              ) : (
                <div className="space-y-4">
                  {/* 1. ConflictBanner (when conflicts is not empty) */}
                  {resp.conflicts && resp.conflicts.length > 0 && (
                    <ConflictBanner conflicts={resp.conflicts} />
                  )}

                  {/* 2. Answer text with clickable [n] chips */}
                  <div className="text-sm text-slate-800 dark:text-slate-200 leading-relaxed font-normal">
                    {renderFormattedAnswer(resp.answer, resp.citations)}
                  </div>

                  {/* 3. ConfidenceBadge */}
                  <div className="flex items-center gap-3 pt-1">
                    <ConfidenceBadge confidence={resp.confidence} />
                  </div>

                  {/* 4. ExpandedTerms (when not empty) */}
                  {resp.expanded_terms && Object.keys(resp.expanded_terms).length > 0 && (
                    <ExpandedTerms terms={resp.expanded_terms} />
                  )}

                  {/* 5. Row of source chips (title, source type, version) */}
                  {resp.citations && resp.citations.length > 0 && (
                    <div className="pt-2">
                      <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-1.5">
                        Verified Sources ({resp.citations.length})
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {resp.citations.map((cite, cIdx) => (
                          <button
                            key={cIdx}
                            type="button"
                            onClick={() => setActiveCitation(cite)}
                            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/80 hover:bg-slate-100 dark:hover:bg-slate-700/80 text-xs text-slate-700 dark:text-slate-300 transition text-left"
                          >
                            <span className="font-mono font-bold text-indigo-600 dark:text-indigo-400">
                              [{cIdx + 1}]
                            </span>
                            <span className="font-medium truncate max-w-[180px]">
                              {cite.title || cite.doc_id}
                            </span>
                            <span className="text-[10px] text-slate-400 uppercase">
                              {cite.source_type}
                            </span>
                            <span className="text-[10px] px-1 py-0.2 rounded bg-slate-200 dark:bg-slate-700 font-mono">
                              {cite.version || 'v1'}
                            </span>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* 6. Experts as small chips when present */}
                  {resp.experts && resp.experts.length > 0 && (
                    <div className="pt-1">
                      <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-1">
                        Domain Experts
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {resp.experts.map((exp, eIdx) => (
                          <span
                            key={eIdx}
                            className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-emerald-50 text-emerald-800 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800"
                          >
                            👤 {exp.name || exp}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* 7. Saved minutes badge + latency */}
                  <div className="flex items-center justify-between pt-3 border-t border-slate-100 dark:border-slate-800 text-xs text-slate-500 dark:text-slate-400">
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-medium">
                      ⏱ saved about {resp.minutes_saved != null ? Number(resp.minutes_saved).toFixed(1) : '9.0'} minutes (estimate)
                    </span>
                    {resp.latency_ms != null && (
                      <span className="text-[11px] font-mono text-slate-400">
                        {resp.latency_ms} ms
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Slide-out CitationPanel */}
      <CitationPanel
        citation={activeCitation}
        onClose={() => setActiveCitation(null)}
      />
    </div>
  );
}
