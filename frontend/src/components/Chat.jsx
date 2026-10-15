import React, { useState, useEffect, useRef } from 'react';
import { useRole } from '../context/RoleContext';
import * as api from '../api';
import ConflictBanner from './ConflictBanner';
import ConfidenceBadge from './ConfidenceBadge';
import ExpandedTerms from './ExpandedTerms';
import IDontKnowCard from './IDontKnowCard';
import CitationPanel from './CitationPanel';
import { SourceTypeIcon, normalizeSourceType } from './SourceTypeBadge';

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
  const inputRef = useRef(null);

  // Clear citation/error when role switches
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
      setHistory((prev) => [
        ...prev,
        {
          id: Date.now(),
          question: q,
          role,
          response: resp,
        },
      ]);
      setQuestion('');
    } catch (err) {
      console.error('Ask query failed:', err);
      setError(err.message || 'Failed to reach backend knowledge service.');
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

  // Clickable [n] citation chips
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
            title={
              cite
                ? `Inspect citation [${citeNum}]: ${cite.title || cite.doc_id}`
                : `Citation [${citeNum}]`
            }
            className="inline-flex items-center justify-center min-w-[20px] h-5 px-1.5 mx-0.5 rounded-full text-[11px] font-mono font-bold bg-[var(--accent-soft)] text-[var(--accent)] hover:bg-[var(--accent)] hover:text-white border border-[var(--accent)]/30 transition-all duration-150 align-baseline cursor-pointer shadow-2xs"
          >
            [{citeNum}]
          </button>
        );
      }
      return <span key={index}>{part}</span>;
    });
  };

  return (
    <div className="max-w-[860px] mx-auto space-y-6">
      {/* Search Input Box with Internal Send Button */}
      <div className="bg-[var(--surface)] rounded-2xl shadow-soft-sm border border-[var(--border)] p-5 sm:p-6 space-y-4">
        <div>
          <label
            htmlFor="question-input"
            className="block text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)] mb-2"
          >
            Ask Knowledge Assistant · <span className="font-mono text-[var(--accent)]">{role.toUpperCase()} CLEARANCE</span>
          </label>

          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSubmit();
            }}
            className="relative flex items-center rounded-xl bg-[var(--surface-2)] border border-[var(--border)] focus-within:ring-2 focus-within:ring-[var(--accent)] focus-within:border-transparent transition-all shadow-soft-sm"
          >
            <input
              id="question-input"
              ref={inputRef}
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
              placeholder="e.g. What temperature should vaccine batches be stored at?"
              className="w-full bg-transparent pl-4 sm:pl-5 pr-28 py-3.5 text-sm sm:text-base text-[var(--text)] placeholder:text-[var(--text-muted)]/60 focus:outline-none"
            />
            <button
              type="submit"
              disabled={loading || !question.trim()}
              className="absolute right-2 px-4 py-2 rounded-lg bg-[var(--accent)] hover:bg-[var(--accent-hover)] disabled:opacity-40 text-white font-medium text-xs sm:text-sm flex items-center gap-1.5 shadow-soft-sm transition-all duration-150 focus-visible:ring-2 focus-visible:ring-[var(--accent)]"
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-3.5 w-3.5 text-white" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                  </svg>
                  <span>Searching...</span>
                </>
              ) : (
                <>
                  <span>Ask</span>
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                  </svg>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Example Questions as Wrapping Chips */}
        <div className="space-y-2 pt-1">
          <div className="text-[11px] font-semibold text-[var(--text-muted)] uppercase tracking-wider">
            Example Queries:
          </div>
          <div className="flex flex-wrap gap-2">
            {EXAMPLE_QUESTIONS.map((ex, i) => (
              <button
                key={i}
                type="button"
                onClick={() => {
                  setQuestion(ex);
                  handleSubmit(ex);
                }}
                disabled={loading}
                className="text-xs px-3 py-1.5 rounded-xl bg-[var(--surface-2)] hover:bg-[var(--accent-soft)] hover:text-[var(--accent)] text-[var(--text)] border border-[var(--border)] text-left transition-all duration-150 disabled:opacity-50 focus-visible:ring-2 focus-visible:ring-[var(--accent)]"
              >
                {ex}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Error state alert */}
      {error && (
        <div
          role="alert"
          className="p-4 rounded-xl border border-[#C4483E]/40 bg-[#FBEEEC] dark:bg-[#381310] text-[#C4483E] dark:text-[#F79B95] text-xs sm:text-sm flex items-center justify-between shadow-soft-sm"
        >
          <div className="flex items-center gap-2">
            <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{error}</span>
          </div>
          <button
            type="button"
            onClick={() => setError(null)}
            className="text-xs underline ml-4 hover:opacity-80"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Loading Skeleton / Typing Indicator */}
      {loading && (
        <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-soft-sm space-y-4 animate-pulse">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-[var(--surface-2)] flex items-center justify-center">
              <span className="w-2.5 h-2.5 rounded-full bg-[var(--accent)] animate-ping" />
            </div>
            <div>
              <div className="text-sm font-semibold text-[var(--text)]">
                Synthesizing verified passages...
              </div>
              <div className="text-xs text-[var(--text-muted)]">
                Filtering by {role} security clearance and scanning for compliance conflicts
              </div>
            </div>
          </div>
          <div className="space-y-2 pt-2">
            <div className="h-3.5 bg-[var(--surface-2)] rounded w-5/6" />
            <div className="h-3.5 bg-[var(--surface-2)] rounded w-4/6" />
            <div className="h-3.5 bg-[var(--surface-2)] rounded w-2/6" />
          </div>
        </div>
      )}

      {/* Conversation History */}
      <div className="space-y-6">
        {history.length === 0 && !loading && (
          <div className="text-center py-12 px-6 rounded-2xl bg-[var(--surface)] border border-dashed border-[var(--border)] space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-[var(--accent-soft)] text-[var(--accent)] flex items-center justify-center mx-auto shadow-soft-sm">
              <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4" />
              </svg>
            </div>
            <h3 className="text-lg font-display font-semibold text-[var(--text)]">
              Audit-Ready Enterprise Answers
            </h3>
            <p className="text-xs text-[var(--text-muted)] max-w-md mx-auto leading-relaxed">
              Every response is verified against active SOPs, policies, and emails. Discrepancies and superseded versions are automatically flagged.
            </p>
          </div>
        )}

        {history.map((item) => {
          const resp = item.response;
          const isAnswerable = resp && resp.answerable;

          return (
            <div
              key={item.id}
              className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-soft-sm space-y-4"
            >
              {/* Question bubble */}
              <div className="flex items-center justify-between border-b border-[var(--border)] pb-3">
                <div className="flex items-center gap-2.5">
                  <span className="w-2 h-2 rounded-full bg-[var(--accent)]" />
                  <span className="text-sm sm:text-base font-semibold text-[var(--text)]">
                    {item.question}
                  </span>
                </div>
                <span className="text-[11px] uppercase tracking-wider font-mono px-2 py-0.5 rounded-full bg-[var(--surface-2)] text-[var(--text-muted)] border border-[var(--border)]">
                  {item.role}
                </span>
              </div>

              {/* If NOT answerable, show IDontKnowCard */}
              {!isAnswerable ? (
                <IDontKnowCard missingInfo={resp?.missing_info} />
              ) : (
                <div className="space-y-4">
                  {/* 1. ConflictBanner */}
                  {resp.conflicts && resp.conflicts.length > 0 && (
                    <ConflictBanner conflicts={resp.conflicts} />
                  )}

                  {/* 2. Formatted Answer Text with Clickable [n] Chips */}
                  <div className="text-sm sm:text-[15px] text-[var(--text)] leading-relaxed font-normal">
                    {renderFormattedAnswer(resp.answer, resp.citations)}
                  </div>

                  {/* 3. Confidence Badge */}
                  <div className="flex items-center gap-3 pt-1">
                    <ConfidenceBadge confidence={resp.confidence} />
                  </div>

                  {/* 4. Expanded Glossary Terms */}
                  {resp.expanded_terms && Object.keys(resp.expanded_terms).length > 0 && (
                    <ExpandedTerms terms={resp.expanded_terms} />
                  )}

                  {/* 5. Verified Sources Chips */}
                  {resp.citations && resp.citations.length > 0 && (
                    <div className="pt-2">
                      <div className="text-[11px] font-semibold uppercase tracking-wider text-[var(--text-muted)] mb-2">
                        Verified Sources ({resp.citations.length})
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {resp.citations.map((cite, cIdx) => (
                          <button
                            key={cIdx}
                            type="button"
                            onClick={() => setActiveCitation(cite)}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-[var(--border)] bg-[var(--surface-2)] hover:bg-[var(--accent-soft)] hover:border-[var(--accent)]/40 text-xs text-[var(--text)] transition-all duration-150 text-left focus-visible:ring-2 focus-visible:ring-[var(--accent)]"
                          >
                            <span className="font-mono font-bold text-[var(--accent)]">
                              [{cIdx + 1}]
                            </span>
                            <span className="font-medium truncate max-w-[200px]">
                              {cite.title || cite.doc_id}
                            </span>
                            <span className="inline-flex items-center gap-1 text-[11px] font-mono px-1.5 py-0.5 rounded bg-[var(--surface)] text-[var(--text-muted)] border border-[var(--border)]">
                              <SourceTypeIcon type={cite.source_type} className="w-3 h-3 text-[var(--accent)] shrink-0" />
                              <span>{normalizeSourceType(cite.source_type)}</span>
                            </span>
                            <span className="text-[11px] px-1.5 py-0.5 rounded bg-[var(--surface)] font-mono text-[var(--text-muted)] border border-[var(--border)]">
                              {cite.version || 'v1.0'}
                            </span>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* 6. Experts Chips */}
                  {resp.experts && resp.experts.length > 0 && (
                    <div className="pt-1">
                      <div className="text-[11px] font-semibold uppercase tracking-wider text-[var(--text-muted)] mb-1.5">
                        Domain Experts
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {resp.experts.map((exp, eIdx) => (
                          <span
                            key={eIdx}
                            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs bg-[#E6F4EE] text-[#1A634E] border border-[#2E8B6E]/30 dark:bg-[#0D2B22] dark:text-[#7FE4C4]"
                          >
                            <span className="w-1.5 h-1.5 rounded-full bg-[#2E8B6E]" />
                            <span>{exp.name || exp}</span>
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* 7. Estimated Minutes Saved + Latency */}
                  <div className="flex items-center justify-between pt-3 border-t border-[var(--border)]/70 text-xs text-[var(--text-muted)]">
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[var(--surface-2)] text-[var(--text)] font-medium border border-[var(--border)]">
                      <span>⏱ Saved about {resp.minutes_saved != null ? Number(resp.minutes_saved).toFixed(1) : '9.0'} minutes</span>
                      <span className="text-[10px] text-[var(--text-muted)]">(estimate)</span>
                    </span>
                    {resp.latency_ms != null && (
                      <span className="text-[11px] font-mono text-[var(--text-muted)]">
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

      {/* Citation Slide-over / Bottom Sheet */}
      <CitationPanel
        citation={activeCitation}
        onClose={() => setActiveCitation(null)}
      />
    </div>
  );
}
