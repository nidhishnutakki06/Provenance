import React from 'react';
import StalenessTag from './StalenessTag';

export default function CitationPanel({ citation, onClose }) {
  if (!citation) return null;

  return (
    <aside
      aria-label="Citation Details"
      className="fixed inset-y-0 right-0 w-full sm:w-96 bg-white dark:bg-slate-900 shadow-2xl border-l border-slate-200 dark:border-slate-800 z-50 flex flex-col transform transition-transform duration-200 ease-in-out"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-850">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            Citation Inspector
          </span>
          <span className="px-2 py-0.5 rounded text-xs font-mono font-bold bg-indigo-100 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300">
            {citation.doc_id || 'DOC'}
          </span>
        </div>
        <button
          onClick={onClose}
          className="rounded-lg p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-200/60 dark:hover:bg-slate-800 transition-colors"
          title="Close citation panel"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto p-5 space-y-5">
        <div>
          <h3 className="text-lg font-bold text-slate-900 dark:text-white leading-snug">
            {citation.title || citation.doc_id || 'Untitled Document'}
          </h3>
          <div className="flex flex-wrap items-center gap-2 mt-3">
            {citation.source_type && (
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 uppercase tracking-wide">
                {citation.source_type}
              </span>
            )}
            <StalenessTag status={citation.status} />
          </div>
        </div>

        {/* Metadata Details */}
        <div className="rounded-lg border border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-850/50 p-3.5 text-xs space-y-2">
          <div className="flex justify-between">
            <span className="text-slate-500 dark:text-slate-400">Document ID:</span>
            <span className="font-mono font-medium text-slate-700 dark:text-slate-300">{citation.doc_id || 'N/A'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500 dark:text-slate-400">Version:</span>
            <span className="font-semibold text-slate-700 dark:text-slate-300">{citation.version || 'N/A'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500 dark:text-slate-400">Effective Date:</span>
            <span className="font-medium text-slate-700 dark:text-slate-300">{citation.date || 'N/A'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500 dark:text-slate-400">Location / Section:</span>
            <span className="font-medium text-slate-700 dark:text-slate-300 text-right">{citation.location || 'N/A'}</span>
          </div>
        </div>

        {/* Highlighted Passage Snippet */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
              Exact Quoted Passage
            </span>
            <span className="text-[11px] text-slate-400 dark:text-slate-500">
              Verified ground truth
            </span>
          </div>
          <div className="rounded-lg border-2 border-indigo-200 dark:border-indigo-900 bg-indigo-50/60 dark:bg-indigo-950/30 p-4 text-xs sm:text-sm text-slate-800 dark:text-slate-200 leading-relaxed font-serif italic shadow-inner">
            "{citation.snippet || 'No excerpt available.'}"
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-850 text-right">
        <button
          onClick={onClose}
          className="px-4 py-2 rounded-lg text-xs font-medium bg-slate-200 hover:bg-slate-300 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 transition-colors"
        >
          Close Inspector
        </button>
      </div>
    </aside>
  );
}
