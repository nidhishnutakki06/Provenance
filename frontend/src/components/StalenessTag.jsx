import React from 'react';

export default function StalenessTag({ status, variant = 'soft' }) {
  const normStatus = (status || '').toLowerCase().trim();

  let label = 'Current';
  let isCurrent = true;
  let isSuperseded = false;

  if (normStatus === 'superseded') {
    label = 'Superseded';
    isCurrent = false;
    isSuperseded = true;
  } else if (normStatus === 'draft') {
    label = 'Draft';
    isCurrent = false;
  }

  let classes = '';
  let icon = null;

  if (variant === 'solid') {
    if (isSuperseded) {
      classes = 'bg-[#C4483E] text-white border-transparent';
      icon = (
        <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    } else if (isCurrent) {
      classes = 'bg-[#2E8B6E] text-white border-transparent';
      icon = (
        <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
        </svg>
      );
    } else {
      classes = 'bg-[var(--neutral)] text-white border-transparent';
      icon = (
        <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
          <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
        </svg>
      );
    }
  } else {
    // soft variant
    if (isSuperseded) {
      classes = 'bg-[var(--danger-soft)] text-[var(--danger-text)] border-[var(--danger-border)]';
      icon = (
        <svg className="w-3 h-3 text-[var(--danger-text)]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    } else if (isCurrent) {
      classes = 'bg-[var(--success-soft)] text-[var(--success-text)] border-[var(--success-border)]';
      icon = (
        <svg className="w-3 h-3 text-[var(--success-text)]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
        </svg>
      );
    } else {
      classes = 'bg-[var(--surface-2)] text-[var(--text-muted)] border-[var(--border)]';
      icon = (
        <svg className="w-3 h-3 text-[var(--text-muted)]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
          <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
        </svg>
      );
    }
  }

  return (
    <span
      className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold border tracking-wide uppercase font-mono shadow-2xs ${classes}`}
    >
      {icon}
      <span>{label}</span>
    </span>
  );
}
