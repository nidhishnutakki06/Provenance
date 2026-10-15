import React from 'react';

export default function ExpandedTerms({ terms }) {
  if (!terms || typeof terms !== 'object') return null;
  const entries = Object.entries(terms);
  if (entries.length === 0) return null;

  return (
    <div className="flex flex-wrap items-center gap-2 pt-1">
      <span className="text-[11px] font-semibold uppercase tracking-wider text-[var(--text-muted)]">
        Glossary Expansion:
      </span>
      {entries.map(([abbr, full]) => (
        <span
          key={abbr}
          className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-xl text-xs font-medium bg-[var(--accent-soft)] text-[var(--text)] border border-[var(--accent)]/20"
          title={`${abbr}: ${full}`}
        >
          <span className="font-bold text-[var(--accent)] font-mono">{abbr}</span>
          <span className="text-[var(--text-muted)] text-[10px]">→</span>
          <span className="text-[var(--text)]">{full}</span>
        </span>
      ))}
    </div>
  );
}
