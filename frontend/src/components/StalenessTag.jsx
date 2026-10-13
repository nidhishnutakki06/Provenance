import React from 'react';

export default function StalenessTag({ status }) {
  const normStatus = (status || '').toLowerCase().trim();

  let label = 'Current';
  let classes = 'bg-emerald-100 text-emerald-800 border-emerald-300 dark:bg-emerald-950/50 dark:text-emerald-300 dark:border-emerald-800';

  if (normStatus === 'superseded') {
    label = 'Superseded';
    classes = 'bg-rose-100 text-rose-800 border-rose-300 dark:bg-rose-950/50 dark:text-rose-300 dark:border-rose-800';
  } else if (normStatus === 'draft') {
    label = 'Draft';
    classes = 'bg-slate-100 text-slate-700 border-slate-300 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700';
  }

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold border ${classes}`}>
      {label}
    </span>
  );
}
