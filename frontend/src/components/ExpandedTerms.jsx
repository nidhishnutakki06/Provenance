import React from 'react';

export default function ExpandedTerms({ terms }) {
  if (!terms || typeof terms !== 'object') return null;
  const entries = Object.entries(terms);
  if (entries.length === 0) return null;

  return (
    <div className="flex flex-wrap items-center gap-2 pt-2">
      <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
        Glossary:
      </span>
      {entries.map(([abbr, full]) => (
        <span
          key={abbr}
          className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-indigo-50 text-indigo-700 border border-indigo-200 dark:bg-indigo-950/40 dark:text-indigo-300 dark:border-indigo-800"
          title={`${abbr}: ${full}`}
        >
          <span className="font-bold text-indigo-900 dark:text-indigo-200">{abbr}</span>
          <span className="text-indigo-400 dark:text-indigo-500">→</span>
          <span>{full}</span>
        </span>
      ))}
    </div>
  );
}
