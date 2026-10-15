import React, { useEffect, useRef } from 'react';
import ReactDOM from 'react-dom';
import StalenessTag from './StalenessTag';
import SourceTypeBadge from './SourceTypeBadge';
import { formatSnippet } from './ConflictBanner';

export default function CitationPanel({ citation, onClose }) {
  const panelRef = useRef(null);
  const triggerElementRef = useRef(null);

  // Focus management, body scroll lock, Escape key, and focus trap
  useEffect(() => {
    if (!citation) return;

    // Save triggering element to return focus on close
    triggerElementRef.current = document.activeElement;

    // Lock body scroll
    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    // Focus the panel or its close button on open
    const timer = setTimeout(() => {
      const focusable = panelRef.current?.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      if (focusable && focusable.length > 0) {
        focusable[0].focus();
      } else {
        panelRef.current?.focus();
      }
    }, 50);

    const handleKeyDown = (e) => {
      // Escape key to close
      if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
        return;
      }

      // Trap focus inside modal
      if (e.key === 'Tab' && panelRef.current) {
        const focusables = panelRef.current.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        if (!focusables || focusables.length === 0) return;

        const firstElement = focusables[0];
        const lastElement = focusables[focusables.length - 1];

        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            e.preventDefault();
            lastElement.focus();
          }
        } else {
          if (document.activeElement === lastElement) {
            e.preventDefault();
            firstElement.focus();
          }
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      clearTimeout(timer);
      document.body.style.overflow = originalOverflow;
      window.removeEventListener('keydown', handleKeyDown);

      // Return focus to trigger element
      if (triggerElementRef.current && typeof triggerElementRef.current.focus === 'function') {
        triggerElementRef.current.focus();
      }
    };
  }, [citation, onClose]);

  if (!citation) return null;

  const content = (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="citation-inspector-title"
      className="fixed inset-0 z-[60] overflow-hidden"
    >
      {/* Full-viewport Backdrop covering header (z-60) */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-xs transition-opacity duration-200"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Drawer / Bottom Sheet Container (z-70) */}
      <aside
        ref={panelRef}
        tabIndex="-1"
        aria-label="Citation Details"
        className="fixed z-[70] bg-[var(--surface)] shadow-2xl border-[var(--border)] flex flex-col focus:outline-none transition-transform duration-200 ease-out
          inset-x-0 bottom-0 max-h-[90dvh] sm:max-h-none rounded-t-3xl sm:rounded-none
          sm:inset-y-0 sm:right-0 sm:left-auto sm:top-0 sm:bottom-0 sm:h-[100dvh] sm:w-[min(480px,100vw)] sm:border-l
          pb-[max(1rem,env(safe-area-inset-bottom))]"
      >
        {/* Mobile drag handle */}
        <div className="sm:hidden w-12 h-1 bg-[var(--border)] rounded-full mx-auto my-2.5 shrink-0" />

        {/* Sticky Top Bar */}
        <div className="sticky top-0 bg-[var(--surface)] z-10 border-b border-[var(--border)] px-5 py-4 flex items-start justify-between gap-3 shadow-2xs">
          <div className="space-y-1.5 flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-[0.06em] text-[var(--text-muted)]">
                Citation Inspector
              </span>
              <span className="px-2 py-0.5 rounded text-xs font-mono font-bold bg-[var(--accent-soft)] text-[var(--accent)] border border-[var(--accent)]/30">
                {citation.doc_id || 'DOC'}
              </span>
            </div>

            <h3
              id="citation-inspector-title"
              className="text-lg sm:text-xl font-display font-semibold text-[var(--text)] leading-snug tracking-tight truncate"
              title={citation.title || citation.doc_id}
            >
              {citation.title || citation.doc_id || 'Document Citation'}
            </h3>

            <div className="flex flex-wrap items-center gap-2 pt-0.5">
              <SourceTypeBadge type={citation.source_type} />
              <StalenessTag status={citation.status} />
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            aria-label="Close citation inspector"
            className="rounded-xl p-2 text-[var(--text-muted)] hover:text-[var(--text)] hover:bg-[var(--surface-2)] transition-colors focus-visible:ring-2 focus-visible:ring-[var(--accent)] shrink-0"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Scrolling Body */}
        <div className="flex-1 overflow-y-auto p-5 sm:p-6 space-y-5">
          {/* Metadata Card */}
          <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-2)] p-4 text-xs font-mono space-y-2.5">
            <div className="flex justify-between items-center">
              <span className="text-[var(--text-muted)] font-sans">Document ID:</span>
              <span className="font-semibold text-[var(--text)]">{citation.doc_id || 'N/A'}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[var(--text-muted)] font-sans">Version:</span>
              <span className="font-semibold text-[var(--text)]">{citation.version || 'v1.0'}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[var(--text-muted)] font-sans">Effective Date:</span>
              <span className="text-[var(--text)]">{citation.date || 'N/A'}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[var(--text-muted)] font-sans">Location / Section:</span>
              <span className="font-medium text-[var(--text)] text-right">{citation.location || 'N/A'}</span>
            </div>
          </div>

          {/* Quoted Passage */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-[0.06em] text-[var(--text)]">
                Exact Quoted Passage
              </span>
              <span className="text-xs font-mono text-[var(--accent)] font-medium">
                Verified ground truth
              </span>
            </div>

            <blockquote className="rounded-xl border-l-4 border-l-[var(--accent)] border border-[var(--border)] bg-[var(--surface-2)]/60 p-4 text-[15px] leading-[1.7] font-sans text-[var(--text)] italic shadow-soft-sm">
              {formatSnippet(citation.snippet || 'No excerpt available.')}
            </blockquote>
          </div>
        </div>

        {/* Sticky Bottom Bar */}
        <div className="sticky bottom-0 bg-[var(--surface-2)] border-t border-[var(--border)] px-5 py-3.5 flex items-center justify-end z-10 shrink-0">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold bg-[var(--surface)] hover:bg-[var(--border)] text-[var(--text)] border border-[var(--border)] transition-colors focus-visible:ring-2 focus-visible:ring-[var(--accent)] shadow-2xs"
          >
            Close Inspector
          </button>
        </div>
      </aside>
    </div>
  );

  return ReactDOM.createPortal(content, document.body);
}
