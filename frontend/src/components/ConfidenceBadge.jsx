import React from 'react';

export default function ConfidenceBadge({ confidence }) {
  const normConf = (confidence || '').toLowerCase().trim();

  let label = 'Low Confidence';
  let badgeClasses =
    'bg-[#FBEEEC] text-[#9B2B23] border-[#C4483E]/30 dark:bg-[#381310] dark:text-[#F79B95] dark:border-[#C4483E]/50';
  let dotColor = 'bg-[#C4483E]';

  if (normConf === 'high') {
    label = 'High Confidence';
    badgeClasses =
      'bg-[#E6F4EE] text-[#1A634E] border-[#2E8B6E]/30 dark:bg-[#0D2B22] dark:text-[#7FE4C4] dark:border-[#2E8B6E]/50';
    dotColor = 'bg-[#2E8B6E]';
  } else if (normConf === 'medium') {
    label = 'Medium Confidence';
    badgeClasses =
      'bg-[#FCF5E8] text-[#875608] border-[#C98A1B]/30 dark:bg-[#382506] dark:text-[#F6C774] dark:border-[#C98A1B]/50';
    dotColor = 'bg-[#C98A1B]';
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border ${badgeClasses}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${dotColor}`} />
      <span>{label}</span>
    </span>
  );
}
