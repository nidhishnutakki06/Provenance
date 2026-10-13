import React, { useState } from 'react';
import { useRole } from '../context/RoleContext';
import { DEMO_USERS } from '../auth/users';

const ROLE_DESCRIPTIONS = {
  intern: 'Intern clearance: Authorized for standard SOPs and onboarding guides (7 docs). Restricted audit and CAPA records are hidden.',
  analyst: 'Analyst clearance: Authorized for technical operations, CAPAs, deviations, and SOPs (18 docs). Confidential executive audits excluded.',
  manager: 'Manager clearance: Full unrestricted enterprise visibility across all 20 documents, confidential audits (AUD-001), and executive emails.',
};

export default function Login() {
  const { login } = useRole();
  const [selectedUserId, setSelectedUserId] = useState(DEMO_USERS[0].id);
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const selectedAccount = DEMO_USERS.find((u) => u.id === selectedUserId) || DEMO_USERS[0];

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    setError('');

    const success = login(selectedUserId, password);
    if (!success) {
      setError('Incorrect password');
    }
  };

  const handleSelectUser = (id) => {
    setSelectedUserId(id);
    setPassword('');
    setError('');
  };

  const handleFillDemo = (user) => {
    setSelectedUserId(user.id);
    setPassword(user.password);
    setError('');
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        {/* Header / Branding */}
        <div className="text-center">
          <span className="text-4xl inline-block mb-2">🛡️</span>
          <div className="flex items-center justify-center gap-2">
            <h1 className="text-2xl font-black tracking-tight text-slate-950 dark:text-white">
              Provenance
            </h1>
            <span className="text-[11px] px-2 py-0.5 rounded-full font-semibold bg-indigo-50 text-indigo-700 dark:bg-indigo-950/80 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
              Novacure Labs
            </span>
          </div>
          <p className="mt-2 text-xs text-slate-500 dark:text-slate-400 font-medium italic">
            “Search tells you where. Provenance tells you whether to trust it.”
          </p>
        </div>

        {/* Login Card */}
        <div className="mt-8 bg-white dark:bg-slate-900 py-8 px-6 shadow-sm border border-slate-200 dark:border-slate-800 rounded-2xl sm:px-8 space-y-6">
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Account Selector */}
            <div>
              <label htmlFor="user-select" className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-300 mb-1.5">
                Select Demo Account
              </label>
              <select
                id="user-select"
                value={selectedUserId}
                onChange={(e) => handleSelectUser(e.target.value)}
                className="w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3.5 py-2.5 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                {DEMO_USERS.map((u) => (
                  <option key={u.id} value={u.id}>
                    {u.name}, {u.title} ({u.role.charAt(0).toUpperCase() + u.role.slice(1)})
                  </option>
                ))}
              </select>
            </div>

            {/* Selected Account Role Clearance Preview */}
            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/60 text-xs space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-700 dark:text-slate-200">
                  Access Level:
                </span>
                <span className="capitalize font-bold text-indigo-600 dark:text-indigo-400">
                  {selectedAccount.role}
                </span>
              </div>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">
                {ROLE_DESCRIPTIONS[selectedAccount.role]}
              </p>
            </div>

            {/* Password Input */}
            <div>
              <label htmlFor="password-input" className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-300 mb-1.5">
                Password
              </label>
              <input
                id="password-input"
                type="password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (error) setError('');
                }}
                placeholder="Enter account password"
                className="w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3.5 py-2.5 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            {/* Error Message */}
            {error && (
              <div className="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-xs font-semibold text-rose-700 dark:text-rose-300 flex items-center gap-2">
                <svg className="w-4 h-4 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <span>{error}</span>
              </div>
            )}

            {/* Sign in Button */}
            <button
              type="submit"
              className="w-full py-2.5 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              Sign in to Provenance
            </button>
          </form>

          {/* Demo Accounts Box for Jury */}
          <div className="pt-4 border-t border-slate-100 dark:border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                Demo Accounts (Click to Autofill)
              </span>
            </div>

            <div className="space-y-1.5">
              {DEMO_USERS.map((u) => (
                <button
                  key={u.id}
                  type="button"
                  onClick={() => handleFillDemo(u)}
                  className="w-full flex items-center justify-between p-2 rounded-lg bg-slate-50 dark:bg-slate-800/50 hover:bg-indigo-50 dark:hover:bg-indigo-950/50 border border-slate-200/60 dark:border-slate-700/60 text-left transition group"
                >
                  <div>
                    <div className="text-xs font-semibold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400">
                      {u.name}
                    </div>
                    <div className="text-[11px] text-slate-500 dark:text-slate-400">
                      {u.title} · <span className="capitalize font-mono">{u.role}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300">
                      {u.password}
                    </span>
                  </div>
                </button>
              ))}
            </div>

            <p className="text-[10px] text-slate-400 dark:text-slate-500 italic text-center pt-1">
              * Demo authentication only. In production, role comes from enterprise SSO group membership.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
