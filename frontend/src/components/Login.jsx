import React, { useState } from 'react';
import { useRole } from '../context/RoleContext';
import { DEMO_USERS } from '../auth/users';

const ROLE_DESCRIPTIONS = {
  intern: 'Intern clearance: Standard SOPs and onboarding guides (7 docs). Restricted audit and CAPA records are hidden.',
  analyst: 'Analyst clearance: Technical operations, CAPAs, deviations, and SOPs (18 docs). Executive audits excluded.',
  manager: 'Manager clearance: Full enterprise visibility across all 20 documents, confidential audits (AUD-001), and executive emails.',
};

export default function Login({ toggleTheme, isDark }) {
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
      setError('Incorrect password. Click an account below to autofill demo credentials.');
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
    <div className="min-h-screen bg-[var(--bg)] text-[var(--text)] flex flex-col justify-center items-center py-8 sm:py-12 px-4 sm:px-6 lg:px-8 relative selection:bg-[var(--accent-soft)] selection:text-[var(--text)]">
      {/* Background ambient radial glow */}
      <div className="ambient-glow-layer" aria-hidden="true" />

      {/* Main Container Card (Hero + Login Form) */}
      <div className="relative z-10 w-full max-w-[1020px] mx-auto rounded-3xl overflow-hidden border border-[var(--border)] shadow-soft-lg flex flex-col lg:flex-row bg-[var(--surface)]">
        
        {/* Left: Deep Navy Gradient Hero Panel (No shield icon) */}
        <div className="lg:w-5/12 bg-gradient-to-br from-[#060D1F] via-[#0B152B] to-[#122340] text-[#EAF2FB] p-8 sm:p-10 flex flex-col justify-between relative overflow-hidden border-b lg:border-b-0 lg:border-r border-[#1E3352]">
          {/* Subtle decorative mesh glow */}
          <div className="absolute top-0 right-0 w-72 h-72 bg-gradient-to-br from-[#3FA9F5]/20 to-[#1E4FA8]/30 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20" />
          <div className="absolute bottom-0 left-0 w-64 h-64 bg-[#7CC3CC]/10 rounded-full blur-2xl pointer-events-none -ml-20 -mb-20" />

          {/* Top Brand alone */}
          <div className="relative z-10 space-y-4">
            <div>
              <h1 className="text-3xl sm:text-4xl font-display font-semibold tracking-tight text-white leading-tight">
                Provenance
              </h1>
              <p className="text-xs font-mono text-[#9BB0C7] uppercase tracking-[0.06em] mt-1">
                Trust-First Enterprise Knowledge
              </p>
            </div>

            <div className="pt-2">
              <p className="font-display italic text-lg sm:text-xl text-[#CBDDEC] leading-relaxed">
                “Search tells you where. Provenance tells you whether to trust it.”
              </p>
            </div>
          </div>

          {/* Core Trust Pillars */}
          <div className="relative z-10 pt-8 mt-6 border-t border-[#1E3352]/70 space-y-3 text-xs text-[#9BB0C7]">
            <div className="flex items-start gap-2.5">
              <svg className="w-4 h-4 text-[#4DA8F0] shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
              <span>Verifiable ground-truth citations with exact document excerpts</span>
            </div>
            <div className="flex items-start gap-2.5">
              <svg className="w-4 h-4 text-[#4DA8F0] shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <span>Automated conflict and supersession compliance detection</span>
            </div>
            <div className="flex items-start gap-2.5">
              <svg className="w-4 h-4 text-[#4DA8F0] shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              <span>Role-gated security clearance (Intern, Analyst, Manager)</span>
            </div>
          </div>
        </div>

        {/* Right: Clean Form Panel */}
        <div className="lg:w-7/12 p-8 sm:p-10 flex flex-col justify-between bg-[var(--surface)] space-y-6">
          <div>
            <div className="flex items-center justify-between pb-4 border-b border-[var(--border)]">
              <div>
                <h2 className="text-xl sm:text-2xl font-display font-semibold text-[var(--text)] tracking-tight">
                  Sign in
                </h2>
                <p className="text-xs font-mono text-[var(--accent)] font-medium mt-0.5">
                  Workspace: Novacure Labs
                </p>
              </div>

              {toggleTheme && (
                <button
                  type="button"
                  onClick={toggleTheme}
                  aria-label="Toggle theme"
                  className="p-2 rounded-xl border border-[var(--border)] text-[var(--text-muted)] hover:text-[var(--text)] hover:bg-[var(--surface-2)] transition-colors focus-visible:ring-2 focus-visible:ring-[var(--accent)]"
                  title="Toggle theme"
                >
                  {isDark ? (
                    <svg className="w-4 h-4 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                    </svg>
                  ) : (
                    <svg className="w-4 h-4 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                    </svg>
                  )}
                </button>
              )}
            </div>

            <form onSubmit={handleSubmit} className="mt-6 space-y-4">
              {/* Account Dropdown */}
              <div>
                <label
                  htmlFor="user-select"
                  className="block text-xs font-bold uppercase tracking-[0.06em] text-[var(--text-muted)] mb-1.5"
                >
                  Demo Account
                </label>
                <div className="relative">
                  <select
                    id="user-select"
                    value={selectedUserId}
                    onChange={(e) => handleSelectUser(e.target.value)}
                    className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface-2)] px-3.5 py-2.5 text-sm text-[var(--text)] focus:outline-none focus:ring-2 focus:ring-[var(--accent)] transition-all appearance-none pr-10 cursor-pointer"
                  >
                    {DEMO_USERS.map((u) => (
                      <option key={u.id} value={u.id} className="bg-[var(--surface)] text-[var(--text)]">
                        {u.name} — {u.title} ({u.role.toUpperCase()})
                      </option>
                    ))}
                  </select>
                  <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-[var(--text-muted)]">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>
              </div>

              {/* Role Clearance Preview Card */}
              <div className="p-3 rounded-xl bg-[var(--surface-2)] border border-[var(--border)] text-xs space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-[var(--text)]">Security Clearance:</span>
                  <span className="font-bold uppercase tracking-[0.06em] text-[var(--accent)] font-mono text-[11px]">
                    {selectedAccount.role}
                  </span>
                </div>
                <p className="text-[11px] text-[var(--text-muted)] leading-relaxed">
                  {ROLE_DESCRIPTIONS[selectedAccount.role]}
                </p>
              </div>

              {/* Password Input */}
              <div>
                <label
                  htmlFor="password-input"
                  className="block text-xs font-bold uppercase tracking-[0.06em] text-[var(--text-muted)] mb-1.5"
                >
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
                  placeholder="Enter account password or click demo card below"
                  className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface-2)] px-3.5 py-2.5 text-sm text-[var(--text)] placeholder:text-[var(--text-muted)]/60 focus:outline-none focus:ring-2 focus:ring-[var(--accent)] transition-all"
                />
              </div>

              {/* Error Message */}
              {error && (
                <div
                  role="alert"
                  className="p-3 rounded-xl bg-[var(--danger-soft)] border border-[var(--danger-border)] text-xs font-medium text-[var(--danger-text)] flex items-center gap-2"
                >
                  <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>{error}</span>
                </div>
              )}

              {/* Pill Sign In Button */}
              <button
                type="submit"
                className="w-full py-3 px-6 rounded-full bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white font-medium text-sm shadow-soft-sm transition-all duration-150 focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)] focus-visible:ring-offset-2"
              >
                Sign in to Provenance
              </button>
            </form>
          </div>

          {/* Demo Accounts Box for Jury */}
          <div className="pt-4 border-t border-[var(--border)] space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold uppercase tracking-[0.06em] text-[var(--text-muted)]">
                Demo Accounts (Click to Autofill)
              </span>
              <span className="text-[11px] font-mono text-[var(--text-muted)]">3 clearance levels</span>
            </div>

            <div className="grid grid-cols-1 gap-2">
              {DEMO_USERS.map((u) => {
                const isSelected = selectedUserId === u.id;
                return (
                  <button
                    key={u.id}
                    type="button"
                    onClick={() => handleFillDemo(u)}
                    className={`w-full flex items-center justify-between p-2.5 rounded-xl border text-left transition-all duration-150 group focus-visible:ring-2 focus-visible:ring-[var(--accent)] ${
                      isSelected
                        ? 'bg-[var(--accent-soft)]/60 border-[var(--accent)]/50'
                        : 'bg-[var(--surface-2)] border-[var(--border)] hover:bg-[var(--surface-2)]/80'
                    }`}
                  >
                    <div className="flex items-center gap-2.5">
                      <div className="w-7 h-7 rounded-full bg-[var(--accent)] text-white flex items-center justify-center font-bold text-xs shrink-0 font-mono">
                        {u.name.charAt(0)}
                      </div>
                      <div>
                        <div className="text-xs font-semibold text-[var(--text)] group-hover:text-[var(--accent)] transition-colors">
                          {u.name}
                        </div>
                        <div className="text-[11px] text-[var(--text-muted)]">
                          {u.title} · <span className="capitalize font-mono font-medium">{u.role}</span>
                        </div>
                      </div>
                    </div>

                    <div className="text-right shrink-0">
                      <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-[var(--surface)] text-[var(--text-muted)] border border-[var(--border)] group-hover:border-[var(--accent)]/40">
                        {u.password}
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>

            <p className="text-[10px] text-[var(--text-muted)] italic text-center pt-1">
              * Demo authentication only. In production, role is synchronized from enterprise SSO group claims.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
