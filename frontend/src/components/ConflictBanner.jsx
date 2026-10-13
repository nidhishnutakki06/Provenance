import React from 'react';
import StalenessTag from './StalenessTag';

export default function ConflictBanner({ conflicts }) {
  if (!conflicts || !Array.isArray(conflicts) || conflicts.length === 0) {
    return null;
  }

  return (
    <div className="space-y-4 my-4">
      {conflicts.map((conflict, idx) => {
        const isContradiction = conflict.kind === 'contradiction';
        const kindTitle = isContradiction ? 'Conflicting sources' : 'Outdated source';
        const sourceA = conflict.source_a || {};
        const sourceB = conflict.source_b || {};

        return (
          <div
            key={idx}
            className="rounded-xl border border-amber-300 bg-amber-50/90 dark:border-amber-700/60 dark:bg-amber-950/30 p-5 shadow-sm text-slate-900 dark:text-slate-100 transition-all"
          >
            {/* Header */}
            <div className="flex items-center gap-3 pb-3 border-b border-amber-200 dark:border-amber-800/60">
              <span className="flex h-7 w-7 items-center justify-center rounded-full bg-amber-200 text-amber-900 dark:bg-amber-900/60 dark:text-amber-200 font-bold text-sm">
                ⚠
              </span>
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-amber-800 dark:text-amber-300">
                  Compliance Alert · {kindTitle}
                </span>
                {conflict.topic && (
                  <span className="ml-2 text-xs text-amber-700 dark:text-amber-400 font-medium">
                    ({conflict.topic})
                  </span>
                )}
              </div>
            </div>

            {/* Explanation */}
            <p className="mt-3 text-sm text-slate-800 dark:text-slate-200 leading-relaxed font-normal">
              {conflict.explanation}
            </p>

            {/* Side-by-Side Sources */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-4">
              {/* Source A */}
              <div className="rounded-lg border border-amber-200/80 bg-white/80 dark:border-amber-900/50 dark:bg-slate-900/60 p-3 text-xs space-y-1.5">
                <div className="flex items-start justify-between gap-2">
                  <div className="font-semibold text-slate-900 dark:text-white line-clamp-1">
                    {sourceA.title || sourceA.doc_id || 'Source A'}
                  </div>
                  <StalenessTag status={sourceA.status} />
                </div>
                <div className="text-slate-500 dark:text-slate-400 flex flex-wrap gap-2 text-[11px]">
                  <span>Version: <strong>{sourceA.version || 'N/A'}</strong></span>
                  <span>·</span>
                  <span>Date: <strong>{sourceA.date || 'N/A'}</strong></span>
                  {sourceA.source_type && (
                    <>
                      <span>·</span>
                      <span className="capitalize">{sourceA.source_type}</span>
                    </>
                  )}
                </div>
                {sourceA.snippet && (
                  <p className="mt-1 pt-1 border-t border-slate-100 dark:border-slate-800 text-slate-700 dark:text-slate-300 italic line-clamp-3">
                    "{sourceA.snippet}"
                  </p>
                )}
              </div>

              {/* Source B */}
              <div className="rounded-lg border border-amber-200/80 bg-white/80 dark:border-amber-900/50 dark:bg-slate-900/60 p-3 text-xs space-y-1.5">
                <div className="flex items-start justify-between gap-2">
                  <div className="font-semibold text-slate-900 dark:text-white line-clamp-1">
                    {sourceB.title || sourceB.doc_id || 'Source B'}
                  </div>
                  <StalenessTag status={sourceB.status} />
                </div>
                <div className="text-slate-500 dark:text-slate-400 flex flex-wrap gap-2 text-[11px]">
                  <span>Version: <strong>{sourceB.version || 'N/A'}</strong></span>
                  <span>·</span>
                  <span>Date: <strong>{sourceB.date || 'N/A'}</strong></span>
                  {sourceB.source_type && (
                    <>
                      <span>·</span>
                      <span className="capitalize">{sourceB.source_type}</span>
                    </>
                  )}
                </div>
                {sourceB.snippet && (
                  <p className="mt-1 pt-1 border-t border-slate-100 dark:border-slate-800 text-slate-700 dark:text-slate-300 italic line-clamp-3">
                    "{sourceB.snippet}"
                  </p>
                )}
              </div>
            </div>

            {/* Recommendation in bold */}
            {conflict.recommendation && (
              <div className="mt-4 pt-3 border-t border-amber-200/60 dark:border-amber-800/40 text-xs text-amber-950 dark:text-amber-200 flex items-start gap-2">
                <span className="font-semibold uppercase tracking-wider text-[11px] text-amber-800 dark:text-amber-400">
                  Recommendation:
                </span>
                <span className="font-bold">
                  {conflict.recommendation}
                </span>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
