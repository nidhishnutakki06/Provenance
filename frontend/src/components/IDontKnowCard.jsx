import React from 'react';

export default function IDontKnowCard({ missingInfo }) {
  const message =
    missingInfo ||
    'I do not have access to sufficient verifiable information in the enterprise repository to answer this question accurately.';

  return (
    <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-soft-sm transition-all duration-200">
      <div className="flex items-start gap-4">
        {/* Neutral Icon */}
        <div className="w-10 h-10 rounded-xl bg-[var(--surface-2)] border border-[var(--border)] flex items-center justify-center text-[var(--text-muted)] shrink-0">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>

        <div className="space-y-2.5 flex-1">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h3 className="text-sm font-semibold text-[var(--text)] tracking-tight">
              Information Not Found / Restricted
            </h3>
            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-mono font-medium bg-[var(--surface-2)] text-[var(--text-muted)] border border-[var(--border)]">
              Answerable: false
            </span>
          </div>

          <p className="text-sm text-[var(--text-muted)] leading-relaxed font-normal">
            {message}
          </p>

          <div className="pt-2 text-[11px] text-[var(--text-muted)]/80 border-t border-[var(--border)]/70 flex items-center gap-1.5">
            <svg className="w-3.5 h-3.5 text-[var(--accent)] shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            <span>
              Provenance prioritizes compliance and audit integrity by refusing to hallucinate when verified evidence is absent.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
