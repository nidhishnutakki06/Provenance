import React from 'react';

export default function ConfidenceBadge({ confidence }) {
  const normConf = (confidence || '').toLowerCase().trim();

  let label = 'Low Confidence';
  let badgeColor = 'bg-rose-100 text-rose-800 border-rose-300 dark:bg-rose-950/50 dark:text-rose-300 dark:border-rose-800';
  let dotColor = 'bg-rose-500';

  if (normConf === 'high') {
    label = 'High Confidence';
    badgeColor = 'bg-emerald-100 text-emerald-800 border-emerald-300 dark:bg-emerald-950/50 dark:text-emerald-300 dark:border-emerald-800';
    dotColor = 'bg-emerald-500';
  } else if (normConf === 'medium') {
    label = 'Medium Confidence';
    badgeColor = 'bg-amber-100 text-amber-800 border-amber-300 dark:bg-amber-950/50 dark:text-amber-300 dark:border-amber-800';
    dotColor = 'bg-amber-500';
  }

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border ${badgeColor}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${dotColor}`} />
      {label}
    </span>
  );
}
