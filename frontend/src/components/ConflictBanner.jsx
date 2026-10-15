import React from 'react';
import StalenessTag from './StalenessTag';
import SourceTypeBadge, { SourceTypeIcon, normalizeSourceType } from './SourceTypeBadge';

// Helper for mid-sentence snippets
export function formatSnippet(snippet) {
  if (!snippet) return '';
  let trimmed = String(snippet).trim();
  if (trimmed.startsWith('"') && trimmed.endsWith('"')) {
    trimmed = trimmed.slice(1, -1).trim();
  }
  if (!trimmed) return '';

  const firstChar = trimmed.charAt(0);
  const startsMidSentence = firstChar === firstChar.toLowerCase() && /[a-z]/i.test(firstChar);
  const lastChar = trimmed.charAt(trimmed.length - 1);
  const endsMidSentence = !/[.!?]/.test(lastChar);

  const prefix = startsMidSentence ? '... ' : '';
  const suffix = endsMidSentence ? ' ...' : '';

  return `"${prefix}${trimmed}${suffix}"`;
}

export default function ConflictBanner({ conflicts }) {
  if (!conflicts || !Array.isArray(conflicts) || conflicts.length === 0) {
    return null;
  }

  return (
    <div className="space-y-5 my-5" role="region" aria-label="Compliance Conflicts Detected">
      {conflicts.map((conflict, idx) => {
        const isContradiction = conflict.kind === 'contradiction';
        const kindLabel = isContradiction ? 'Conflicting sources' : 'Outdated source';
        const rawSourceA = conflict.source_a || {};
        const rawSourceB = conflict.source_b || {};

        // Detect if one source is superseded
        const hasSuperseded =
          rawSourceA.status === 'superseded' ||
          rawSourceB.status === 'superseded' ||
          conflict.kind === 'superseded';

        let sourceA = rawSourceA;
        let sourceB = rawSourceB;
        let isSourceASuperseded = rawSourceA.status === 'superseded';

        // Date comparison for "Newer" badge in contradictions
        const dateA = sourceA.date || '';
        const dateB = sourceB.date || '';
        const isANewer = !hasSuperseded && dateA && dateB && dateA > dateB;
        const isBNewer = !hasSuperseded && dateA && dateB && dateB > dateA;

        return (
          <div
            key={idx}
            className="rounded-2xl border-t-4 border-t-[#C98A1B] border border-[var(--border)] bg-[var(--surface)] shadow-soft-sm overflow-hidden text-[var(--text)] transition-all duration-200"
          >
            {/* Header Strip */}
            <div className="flex items-center justify-between px-5 py-3.5 border-b border-[var(--border)] bg-[var(--surface)]">
              <div className="flex items-center gap-2.5">
                <div className="w-7 h-7 rounded-lg bg-[#FCF5E8] dark:bg-[#382506] text-[#C98A1B] flex items-center justify-center shrink-0 border border-[#C98A1B]/30">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold uppercase tracking-[0.06em] text-[var(--text)]">
                    {kindLabel}
                  </span>
                </div>
              </div>

              {conflict.topic && (
                <span className="text-xs font-mono font-medium px-2.5 py-0.5 rounded-full bg-[var(--surface-2)] text-[var(--text-muted)] border border-[var(--border)]">
                  #{conflict.topic}
                </span>
              )}
            </div>

            {/* Explanation paragraph */}
            <div className="px-5 pt-4">
              <p className="text-sm text-[var(--text)] leading-relaxed font-normal">
                {conflict.explanation}
              </p>
            </div>

            {/* Cards layout with round divider */}
            <div className="p-5">
              <div className="relative flex flex-col md:flex-row items-stretch gap-4">
                {/* Source A Card */}
                <div
                  className={`flex-1 rounded-xl p-4 space-y-3 transition-all duration-150 border-l-4 ${
                    hasSuperseded && isSourceASuperseded
                      ? 'bg-[var(--danger-soft)] border-l-[#C4483E] border border-[var(--danger-border)]'
                      : hasSuperseded
                      ? 'bg-[var(--success-soft)] border-l-[#2E8B6E] border border-[var(--success-border)]'
                      : 'bg-[var(--accent-soft)]/60 border-l-[var(--accent)] border border-[var(--border)]'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="space-y-0.5">
                      <div className="flex items-center gap-2">
                        <SourceTypeIcon type={sourceA.source_type} className="w-4 h-4 text-[var(--text-muted)]" />
                        <h4
                          className={`text-sm font-semibold tracking-tight ${
                            hasSuperseded && isSourceASuperseded
                              ? 'text-[var(--text-muted)] opacity-90'
                              : 'text-[var(--text)]'
                          }`}
                        >
                          {sourceA.title || sourceA.doc_id || 'Source A'}
                        </h4>
                      </div>
                      {hasSuperseded && (
                        <div
                          className={`text-[11px] font-bold uppercase tracking-wider ${
                            isSourceASuperseded ? 'text-[var(--danger-text)]' : 'text-[var(--success-text)]'
                          }`}
                        >
                          {isSourceASuperseded ? 'Do not use' : 'Use this'}
                        </div>
                      )}
                    </div>

                    <div className="flex items-center gap-1.5 shrink-0">
                      {isANewer && (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-[var(--accent)] text-white shadow-2xs">
                          Newer
                        </span>
                      )}
                      <StalenessTag
                        status={hasSuperseded ? (isSourceASuperseded ? 'superseded' : 'current') : sourceA.status}
                        variant={hasSuperseded ? 'solid' : 'soft'}
                      />
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-2 text-xs font-mono text-[var(--text-muted)]">
                    <span>
                      Version: <strong className="text-[var(--text)]">{sourceA.version || 'N/A'}</strong>
                    </span>
                    <span>·</span>
                    <span>
                      Date: <strong className="text-[var(--text)]">{sourceA.date || 'N/A'}</strong>
                    </span>
                    {sourceA.source_type && (
                      <>
                        <span>·</span>
                        <SourceTypeBadge type={sourceA.source_type} />
                      </>
                    )}
                  </div>

                  {sourceA.snippet && (
                    <div
                      className={`mt-2 pt-2 text-[15px] leading-[1.7] font-sans italic pl-3 border-l-2 rounded-r-lg py-2 ${
                        hasSuperseded && isSourceASuperseded
                          ? 'border-slate-400 bg-[var(--surface)]/60 text-[var(--text)]'
                          : hasSuperseded
                          ? 'border-[#2E8B6E] bg-[var(--surface)]/70 text-[var(--text)]'
                          : 'border-[var(--accent)] bg-[var(--surface)]/70 text-[var(--text)]'
                      }`}
                    >
                      {formatSnippet(sourceA.snippet)}
                    </div>
                  )}
                </div>

                {/* Round Divider (Arrow for superseded, 'vs' for contradiction) */}
                <div className="self-center flex items-center justify-center shrink-0 z-10">
                  <div className="w-8 h-8 rounded-full bg-[var(--surface)] border border-[var(--border)] shadow-soft-sm flex items-center justify-center text-xs font-mono font-bold text-[var(--text-muted)]">
                    {hasSuperseded ? (
                      <>
                        {/* Right arrow on desktop if A is superseded, else left */}
                        {isSourceASuperseded ? (
                          <svg className="w-4 h-4 hidden md:block text-[#2E8B6E]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                          </svg>
                        ) : (
                          <svg className="w-4 h-4 hidden md:block text-[#2E8B6E]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                          </svg>
                        )}
                        {/* Down arrow on mobile if A is superseded, else up */}
                        <svg className="w-4 h-4 md:hidden text-[#2E8B6E]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                        </svg>
                      </>
                    ) : (
                      <span>vs</span>
                    )}
                  </div>
                </div>

                {/* Source B Card */}
                <div
                  className={`flex-1 rounded-xl p-4 space-y-3 transition-all duration-150 border-l-4 ${
                    hasSuperseded && !isSourceASuperseded
                      ? 'bg-[var(--danger-soft)] border-l-[#C4483E] border border-[var(--danger-border)]'
                      : hasSuperseded
                      ? 'bg-[var(--success-soft)] border-l-[#2E8B6E] border border-[var(--success-border)]'
                      : 'bg-[var(--violet-soft)] border-l-[var(--violet-text)] border border-[var(--border)]'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="space-y-0.5">
                      <div className="flex items-center gap-2">
                        <SourceTypeIcon type={sourceB.source_type} className="w-4 h-4 text-[var(--text-muted)]" />
                        <h4
                          className={`text-sm font-semibold tracking-tight ${
                            hasSuperseded && !isSourceASuperseded
                              ? 'text-[var(--text-muted)] opacity-90'
                              : 'text-[var(--text)]'
                          }`}
                        >
                          {sourceB.title || sourceB.doc_id || 'Source B'}
                        </h4>
                      </div>
                      {hasSuperseded && (
                        <div
                          className={`text-[11px] font-bold uppercase tracking-wider ${
                            !isSourceASuperseded ? 'text-[var(--danger-text)]' : 'text-[var(--success-text)]'
                          }`}
                        >
                          {!isSourceASuperseded ? 'Do not use' : 'Use this'}
                        </div>
                      )}
                    </div>

                    <div className="flex items-center gap-1.5 shrink-0">
                      {isBNewer && (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-[var(--accent)] text-white shadow-2xs">
                          Newer
                        </span>
                      )}
                      <StalenessTag
                        status={hasSuperseded ? (!isSourceASuperseded ? 'superseded' : 'current') : sourceB.status}
                        variant={hasSuperseded ? 'solid' : 'soft'}
                      />
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-2 text-xs font-mono text-[var(--text-muted)]">
                    <span>
                      Version: <strong className="text-[var(--text)]">{sourceB.version || 'N/A'}</strong>
                    </span>
                    <span>·</span>
                    <span>
                      Date: <strong className="text-[var(--text)]">{sourceB.date || 'N/A'}</strong>
                    </span>
                    {sourceB.source_type && (
                      <>
                        <span>·</span>
                        <SourceTypeBadge type={sourceB.source_type} />
                      </>
                    )}
                  </div>

                  {sourceB.snippet && (
                    <div
                      className={`mt-2 pt-2 text-[15px] leading-[1.7] font-sans italic pl-3 border-l-2 rounded-r-lg py-2 ${
                        hasSuperseded && !isSourceASuperseded
                          ? 'border-slate-400 bg-[var(--surface)]/60 text-[var(--text)]'
                          : hasSuperseded
                          ? 'border-[#2E8B6E] bg-[var(--surface)]/70 text-[var(--text)]'
                          : 'border-[var(--violet-text)] bg-[var(--surface)]/70 text-[var(--text)]'
                      }`}
                    >
                      {formatSnippet(sourceB.snippet)}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Recommendation Filled Strip at Bottom */}
            {conflict.recommendation && (
              <div className="px-5 py-3.5 bg-[var(--surface-2)] border-t border-[var(--border)] text-xs sm:text-sm flex items-start gap-2.5">
                <div className="w-5 h-5 rounded-full bg-[#FCF5E8] dark:bg-[#382506] text-[#C98A1B] flex items-center justify-center shrink-0 mt-0.5 border border-[#C98A1B]/30">
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <div className="space-y-0.5">
                  <span className="font-bold uppercase tracking-[0.06em] text-[11px] text-[var(--text-muted)] mr-2">
                    Recommendation:
                  </span>
                  <span className="font-bold text-[var(--text)] leading-relaxed">
                    {conflict.recommendation}
                  </span>
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
