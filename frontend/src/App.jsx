import React, { useState, useEffect, useRef } from 'react';
import { useRole } from './context/RoleContext';
import * as api from './api';
import Login from './components/Login';
import Chat from './components/Chat';
import Onboarding from './components/Onboarding';
import Experts from './components/Experts';
import Dashboard from './components/Dashboard';

const ROLE_DESCRIPTIONS = {
  intern: 'Intern clearance: Standard SOPs and onboarding guides (7 docs). Restricted audit and CAPA records are hidden.',
  analyst: 'Analyst clearance: Technical operations, CAPAs, deviations, and SOPs (18 docs). Executive audits excluded.',
  manager: 'Manager clearance: Full enterprise visibility across all 20 documents, confidential audits (AUD-001), and executive records.',
};

export default function App() {
  const { role, user, logout } = useRole();
  const [activeTab, setActiveTab] = useState('chat'); // 'chat' | 'onboarding-experts' | 'dashboard'
  const [oeSubTab, setOeSubTab] = useState('onboarding'); // 'onboarding' | 'experts'
  const [health, setHealth] = useState(null);
  const [backendError, setBackendError] = useState(null);

  // Theme state: dark / light with localStorage and prefers-color-scheme
  const [isDark, setIsDark] = useState(() => {
    try {
      const saved = localStorage.getItem('provenance_theme');
      if (saved) return saved === 'dark';
      return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    } catch {
      return false;
    }
  });

  useEffect(() => {
    try {
      if (isDark) {
        document.documentElement.classList.add('dark');
        localStorage.setItem('provenance_theme', 'dark');
      } else {
        document.documentElement.classList.remove('dark');
        localStorage.setItem('provenance_theme', 'light');
      }
    } catch (err) {
      console.warn('Failed saving theme preference to localStorage:', err);
    }
  }, [isDark]);

  const toggleTheme = () => setIsDark((prev) => !prev);

  // User menu dropdown state and keyboard/click management
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [healthTooltipOpen, setHealthTooltipOpen] = useState(false);
  const userButtonRef = useRef(null);
  const userMenuRef = useRef(null);
  const switchUserButtonRef = useRef(null);

  useEffect(() => {
    if (!userMenuOpen) return;

    const handleOutsideClick = (e) => {
      if (
        userMenuRef.current &&
        !userMenuRef.current.contains(e.target) &&
        userButtonRef.current &&
        !userButtonRef.current.contains(e.target)
      ) {
        setUserMenuOpen(false);
      }
    };

    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        setUserMenuOpen(false);
        userButtonRef.current?.focus();
      } else if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        switchUserButtonRef.current?.focus();
      }
    };

    document.addEventListener('mousedown', handleOutsideClick);
    window.addEventListener('keydown', handleKeyDown);

    const timer = setTimeout(() => {
      switchUserButtonRef.current?.focus();
    }, 40);

    return () => {
      clearTimeout(timer);
      document.removeEventListener('mousedown', handleOutsideClick);
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [userMenuOpen]);

  // Check backend health
  useEffect(() => {
    let mounted = true;
    const check = async () => {
      try {
        const h = await api.getHealth();
        if (mounted) {
          setHealth(h);
          setBackendError(null);
        }
      } catch (err) {
        if (mounted) {
          console.error('Health check failed:', err);
          setBackendError(
            'Backend is unreachable at ' +
              (import.meta.env.VITE_API_URL || 'http://localhost:8000') +
              '. Please ensure FastAPI server is running.'
          );
          setHealth(null);
        }
      }
    };

    check();
    const interval = setInterval(check, 10000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  // If no user is logged in, show the Login screen
  if (!user) {
    return <Login toggleTheme={toggleTheme} isDark={isDark} />;
  }

  // Health dot state (green: real+groq, amber: mock, red: offline)
  let healthDotColor = 'bg-[#C4483E]'; // Red (offline / unreachable)
  let healthTooltip = 'Backend is offline';

  if (health && health.status === 'ok') {
    if (health.llm === 'mock') {
      healthDotColor = 'bg-[#C98A1B]'; // Amber (mock LLM)
      healthTooltip = `LLM: mock · Data: ${health.data_source} (${health.chunks || 46} chunks)`;
    } else if (health.data_source === 'real' && health.llm === 'groq') {
      healthDotColor = 'bg-[#2E8B6E]'; // Green (real groq)
      healthTooltip = `LLM: groq · Data: real (${health.chunks || 46} chunks)`;
    } else {
      healthDotColor = 'bg-[#2E8B6E]';
      healthTooltip = `LLM: ${health.llm} · Data: ${health.data_source} (${health.chunks || 46} chunks)`;
    }
  }
  const healthAriaLabel = healthTooltip;

  const firstName = user?.name ? user.name.split(' ')[0] : 'User';

  return (
    <div className="min-h-screen flex flex-col bg-[var(--bg)] text-[var(--text)] relative selection:bg-[var(--accent-soft)] selection:text-[var(--text)]">
      {/* Background ambient radial glow */}
      <div className="ambient-glow-layer" aria-hidden="true" />

      {/* Backend unreachable warning bar */}
      {backendError && (
        <div
          role="alert"
          className="relative z-[80] bg-[#C4483E] text-white px-4 py-2 text-center text-xs sm:text-sm font-medium flex items-center justify-center gap-2 shadow-soft-sm"
        >
          <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span>{backendError}</span>
        </div>
      )}

      {/* Slim Sticky Header (~64px desktop, 56px mobile row 1) with ~92% opacity */}
      <header className="sticky top-0 z-40 bg-[var(--bg)]/92 backdrop-blur-md border-b border-[var(--border)] pt-[env(safe-area-inset-top,0px)] transition-colors duration-200">
        <div className="max-w-[1200px] mx-auto px-4 sm:px-6 h-14 lg:h-16 flex items-center justify-between gap-3 sm:gap-4 min-w-0">
          
          {/* Left: Playfair Display Wordmark Alone (no icon) */}
          <div className="flex items-center min-w-0 shrink-0">
            <button
              type="button"
              onClick={() => setActiveTab('chat')}
              className="text-left focus-visible:ring-2 focus-visible:ring-[var(--accent)] rounded-lg transition-transform active:scale-95"
            >
              <span className="text-2xl font-display font-semibold tracking-tight text-[var(--text)] whitespace-nowrap">
                Provenance
              </span>
            </button>
          </div>

          {/* Centre (Desktop 1024px+): Three Tabs in Soft Pill Container (--surface-2, 4px padding) */}
          <div className="hidden lg:flex items-center justify-center flex-1 min-w-0 px-4">
            <nav
              role="tablist"
              aria-label="Application Sections"
              className="inline-flex items-center p-1 rounded-full bg-[var(--surface-2)] border border-[var(--border)] whitespace-nowrap shadow-2xs"
            >
              {/* Tab 1: Chat */}
              <button
                role="tab"
                id="tab-chat"
                aria-selected={activeTab === 'chat'}
                aria-controls="panel-chat"
                onClick={() => setActiveTab('chat')}
                className={`px-4 py-1.5 text-[14px] font-medium font-sans rounded-full flex items-center gap-2 whitespace-nowrap transition-all duration-150 focus-visible:ring-2 focus-visible:ring-[var(--accent)] focus:outline-none ${
                  activeTab === 'chat'
                    ? 'bg-[var(--surface)] text-[var(--accent)] font-semibold shadow-soft-sm'
                    : 'text-[var(--text-muted)] hover:text-[var(--text)]'
                }`}
              >
                <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                <span>Chat</span>
              </button>

              {/* Tab 2: Onboarding */}
              <button
                role="tab"
                id="tab-onboarding"
                aria-selected={activeTab === 'onboarding-experts'}
                aria-controls="panel-onboarding"
                onClick={() => setActiveTab('onboarding-experts')}
                className={`px-4 py-1.5 text-[14px] font-medium font-sans rounded-full flex items-center gap-2 whitespace-nowrap transition-all duration-150 focus-visible:ring-2 focus-visible:ring-[var(--accent)] focus:outline-none ${
                  activeTab === 'onboarding-experts'
                    ? 'bg-[var(--surface)] text-[var(--accent)] font-semibold shadow-soft-sm'
                    : 'text-[var(--text-muted)] hover:text-[var(--text)]'
                }`}
              >
                <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
                <span>Onboarding</span>
              </button>

              {/* Tab 3: Dashboard */}
              <button
                role="tab"
                id="tab-dashboard"
                aria-selected={activeTab === 'dashboard'}
                aria-controls="panel-dashboard"
                onClick={() => setActiveTab('dashboard')}
                className={`px-4 py-1.5 text-[14px] font-medium font-sans rounded-full flex items-center gap-2 whitespace-nowrap transition-all duration-150 focus-visible:ring-2 focus-visible:ring-[var(--accent)] focus:outline-none ${
                  activeTab === 'dashboard'
                    ? 'bg-[var(--surface)] text-[var(--accent)] font-semibold shadow-soft-sm'
                    : 'text-[var(--text-muted)] hover:text-[var(--text)]'
                }`}
              >
                <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <span>Dashboard</span>
              </button>
            </nav>
          </div>

          {/* Right: In exact order (1) Health status dot, (2) User menu button, (3) Theme toggle */}
          <div className="flex items-center gap-2 sm:gap-2.5 shrink-0 min-w-0">
            {/* (1) Health Status Dot with hover/focus Tooltip */}
            <div className="relative group flex items-center order-1">
              <button
                type="button"
                aria-label={healthAriaLabel}
                onMouseEnter={() => setHealthTooltipOpen(true)}
                onMouseLeave={() => setHealthTooltipOpen(false)}
                onFocus={() => setHealthTooltipOpen(true)}
                onBlur={() => setHealthTooltipOpen(false)}
                className="p-1.5 rounded-lg hover:bg-[var(--surface-2)] transition-colors focus-visible:ring-2 focus-visible:ring-[var(--accent)] focus:outline-none flex items-center justify-center cursor-default min-h-[40px] min-w-[40px]"
              >
                <span className={`w-2.5 h-2.5 rounded-full shrink-0 ${healthDotColor} shadow-2xs transition-colors duration-200`} />
                <span className="sr-only">{healthAriaLabel}</span>
              </button>

              <div
                role="tooltip"
                className={`pointer-events-none absolute top-full left-1/2 -translate-x-1/2 mt-2 px-3 py-1.5 rounded-lg bg-[var(--surface)] text-[var(--text)] border border-[var(--border)] shadow-soft-md text-xs font-mono whitespace-nowrap transition-opacity duration-150 z-50 ${
                  healthTooltipOpen ? 'opacity-100' : 'opacity-0 group-hover:opacity-100 group-focus-within:opacity-100'
                }`}
              >
                {healthTooltip}
              </div>
            </div>

            {/* (2) User Menu Button with Dropdown (desktop order-2, mobile order-3) */}
            <div className="relative order-3 lg:order-2">
              <button
                ref={userButtonRef}
                type="button"
                aria-expanded={userMenuOpen}
                aria-haspopup="menu"
                aria-label={`User menu for ${user.name}`}
                onClick={() => setUserMenuOpen((prev) => !prev)}
                className="flex items-center gap-2 p-1 sm:px-2.5 sm:py-1.5 rounded-xl border border-[var(--border)] hover:bg-[var(--surface-2)] transition-all duration-150 focus-visible:ring-2 focus-visible:ring-[var(--accent)] focus:outline-none min-h-[44px] min-w-[44px] sm:min-w-0 justify-center sm:justify-start"
              >
                {/* Initials Avatar */}
                <div className="w-7 h-7 rounded-full bg-[var(--accent)] text-white flex items-center justify-center text-xs font-semibold shrink-0">
                  {user.name ? user.name.charAt(0) : 'U'}
                </div>

                {/* First name (hidden on under 640px) */}
                <span className="text-xs font-medium text-[var(--text)] truncate max-w-[100px] sm:max-w-[120px] hidden sm:inline whitespace-nowrap">
                  {firstName}
                </span>

                {/* Small Role Badge (hidden on under 640px) */}
                <span
                  className={`text-[10px] uppercase font-bold tracking-[0.06em] font-mono px-2 py-0.5 rounded-full border hidden sm:inline-flex whitespace-nowrap ${
                    role === 'intern'
                      ? 'bg-sky-50 text-sky-800 border-sky-200 dark:bg-sky-950/60 dark:text-sky-300 dark:border-sky-800'
                      : role === 'analyst'
                      ? 'bg-blue-50 text-blue-800 border-blue-200 dark:bg-blue-950/60 dark:text-blue-300 dark:border-blue-800'
                      : 'bg-purple-50 text-purple-800 border-purple-200 dark:bg-purple-950/60 dark:text-purple-300 dark:border-purple-800'
                  }`}
                >
                  {role}
                </span>

                {/* Chevron (hidden on under 640px) */}
                <svg
                  className={`w-3.5 h-3.5 text-[var(--text-muted)] transition-transform duration-150 shrink-0 hidden sm:inline-block ${
                    userMenuOpen ? 'rotate-180' : ''
                  }`}
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {/* User Menu Dropdown (right-aligned under button) */}
              {userMenuOpen && (
                <div
                  ref={userMenuRef}
                  role="menu"
                  aria-label="User account and clearance"
                  className="absolute right-0 top-full mt-2 w-72 sm:w-80 rounded-2xl bg-[var(--surface)] border border-[var(--border)] shadow-soft-lg p-4 z-50 focus:outline-none transition-all duration-150"
                >
                  <div className="space-y-1.5">
                    <div className="text-sm font-semibold text-[var(--text)] leading-snug">
                      {user.name}, {user.title}
                    </div>
                    <div className="flex items-center gap-2 pt-0.5">
                      <span
                        className={`text-[10px] uppercase font-bold tracking-[0.06em] font-mono px-2 py-0.5 rounded-full border inline-flex ${
                          role === 'intern'
                            ? 'bg-sky-50 text-sky-800 border-sky-200 dark:bg-sky-950/60 dark:text-sky-300 dark:border-sky-800'
                            : role === 'analyst'
                            ? 'bg-blue-50 text-blue-800 border-blue-200 dark:bg-blue-950/60 dark:text-blue-300 dark:border-blue-800'
                            : 'bg-purple-50 text-purple-800 border-purple-200 dark:bg-purple-950/60 dark:text-purple-300 dark:border-purple-800'
                        }`}
                      >
                        {role}
                      </span>
                    </div>
                    <p className="text-xs text-[var(--text-muted)] leading-relaxed pt-1">
                      {ROLE_DESCRIPTIONS[role] || ''}
                    </p>
                  </div>

                  <div className="border-t border-[var(--border)] my-3" />

                  <button
                    ref={switchUserButtonRef}
                    role="menuitem"
                    type="button"
                    onClick={() => {
                      setUserMenuOpen(false);
                      logout();
                      userButtonRef.current?.focus();
                    }}
                    className="w-full flex items-center justify-between px-3 py-2 text-xs font-semibold rounded-xl text-[var(--text)] hover:text-[#C4483E] hover:bg-[var(--danger-soft)] border border-[var(--border)] hover:border-[var(--danger-border)] transition-colors focus-visible:ring-2 focus-visible:ring-[var(--accent)] min-h-[44px]"
                  >
                    <span>Switch user</span>
                    <svg className="w-4 h-4 shrink-0 text-[var(--text-muted)]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                  </button>
                </div>
              )}
            </div>

            {/* (3) Theme Toggle Button (desktop order-3, mobile order-2) */}
            <button
              type="button"
              onClick={toggleTheme}
              aria-label={isDark ? 'Switch to light theme' : 'Switch to dark theme'}
              className="order-2 lg:order-3 p-2 rounded-xl border border-[var(--border)] text-[var(--text-muted)] hover:text-[var(--text)] hover:bg-[var(--surface-2)] transition-colors focus-visible:ring-2 focus-visible:ring-[var(--accent)] focus:outline-none min-h-[44px] min-w-[44px] flex items-center justify-center shrink-0"
              title={isDark ? 'Switch to light theme' : 'Switch to dark theme'}
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
          </div>
        </div>

        {/* Tablet and Mobile Second Row for Tabs (< 1024px) */}
        <div className="lg:hidden border-t border-[var(--border)] px-4 sm:px-6 py-2 bg-[var(--bg)]/92">
          <div className="max-w-[1200px] mx-auto">
            <nav
              role="tablist"
              aria-label="Application Sections"
              className="grid grid-cols-3 p-1 rounded-full bg-[var(--surface-2)] border border-[var(--border)]"
            >
              <button
                role="tab"
                id="tab-mobile-chat"
                aria-selected={activeTab === 'chat'}
                aria-controls="panel-chat"
                onClick={() => setActiveTab('chat')}
                className={`min-h-[44px] px-2 py-1.5 text-xs sm:text-sm font-medium rounded-full flex items-center justify-center gap-1.5 whitespace-nowrap transition-all duration-150 focus-visible:ring-2 focus-visible:ring-[var(--accent)] focus:outline-none ${
                  activeTab === 'chat'
                    ? 'bg-[var(--surface)] text-[var(--accent)] font-semibold shadow-soft-sm'
                    : 'text-[var(--text-muted)] hover:text-[var(--text)]'
                }`}
              >
                <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                <span className="truncate">Chat</span>
              </button>

              <button
                role="tab"
                id="tab-mobile-onboarding"
                aria-selected={activeTab === 'onboarding-experts'}
                aria-controls="panel-onboarding"
                onClick={() => setActiveTab('onboarding-experts')}
                className={`min-h-[44px] px-2 py-1.5 text-xs sm:text-sm font-medium rounded-full flex items-center justify-center gap-1.5 whitespace-nowrap transition-all duration-150 focus-visible:ring-2 focus-visible:ring-[var(--accent)] focus:outline-none ${
                  activeTab === 'onboarding-experts'
                    ? 'bg-[var(--surface)] text-[var(--accent)] font-semibold shadow-soft-sm'
                    : 'text-[var(--text-muted)] hover:text-[var(--text)]'
                }`}
              >
                <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
                <span className="truncate">Onboarding</span>
              </button>

              <button
                role="tab"
                id="tab-mobile-dashboard"
                aria-selected={activeTab === 'dashboard'}
                aria-controls="panel-dashboard"
                onClick={() => setActiveTab('dashboard')}
                className={`min-h-[44px] px-2 py-1.5 text-xs sm:text-sm font-medium rounded-full flex items-center justify-center gap-1.5 whitespace-nowrap transition-all duration-150 focus-visible:ring-2 focus-visible:ring-[var(--accent)] focus:outline-none ${
                  activeTab === 'dashboard'
                    ? 'bg-[var(--surface)] text-[var(--accent)] font-semibold shadow-soft-sm'
                    : 'text-[var(--text-muted)] hover:text-[var(--text)]'
                }`}
              >
                <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <span className="truncate">Dashboard</span>
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="relative z-10 flex-1 max-w-[1200px] w-full mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-6">
        {/* Quiet Security Clearance Note (Outside header, scrolls away naturally) */}
        <div className="p-3 rounded-xl bg-[var(--surface-2)] border border-[var(--border)] text-xs text-[var(--text-muted)] flex items-center gap-2">
          <span className="font-semibold text-[var(--text)] font-mono uppercase tracking-[0.06em] shrink-0">
            Security Clearance:
          </span>
          <span className="truncate">{ROLE_DESCRIPTIONS[role] || ''}</span>
        </div>

        {activeTab === 'chat' && (
          <div id="panel-chat" role="tabpanel" aria-labelledby="tab-chat">
            <Chat key={`chat-${role}-${user.id}`} />
          </div>
        )}

        {activeTab === 'onboarding-experts' && (
          <div id="panel-onboarding" role="tabpanel" aria-labelledby="tab-onboarding" className="space-y-6">
            {/* Sub-tab segmented pill control */}
            <div className="flex justify-center">
              <div className="inline-flex p-1 rounded-xl bg-[var(--surface-2)] border border-[var(--border)] gap-1">
                <button
                  type="button"
                  onClick={() => setOeSubTab('onboarding')}
                  className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all duration-150 focus-visible:ring-2 focus-visible:ring-[var(--accent)] ${
                    oeSubTab === 'onboarding'
                      ? 'bg-[var(--accent)] text-white shadow-soft-sm'
                      : 'text-[var(--text-muted)] hover:text-[var(--text)]'
                  }`}
                >
                  Curated Onboarding Paths
                </button>
                <button
                  type="button"
                  onClick={() => setOeSubTab('experts')}
                  className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all duration-150 focus-visible:ring-2 focus-visible:ring-[var(--accent)] ${
                    oeSubTab === 'experts'
                      ? 'bg-[var(--accent)] text-white shadow-soft-sm'
                      : 'text-[var(--text-muted)] hover:text-[var(--text)]'
                  }`}
                >
                  Subject Matter Experts
                </button>
              </div>
            </div>

            {oeSubTab === 'onboarding' ? (
              <Onboarding key={`onboarding-${role}-${user.id}`} />
            ) : (
              <Experts key={`experts-${role}-${user.id}`} />
            )}
          </div>
        )}

        {activeTab === 'dashboard' && (
          <div id="panel-dashboard" role="tabpanel" aria-labelledby="tab-dashboard">
            <Dashboard key={`dashboard-${role}-${user.id}`} />
          </div>
        )}
      </main>

      {/* Muted Footer */}
      <footer className="relative z-10 mt-auto border-t border-[var(--border)] bg-[var(--surface)]/70 backdrop-blur-sm py-4">
        <div className="max-w-[1200px] mx-auto px-4 sm:px-6 text-center text-xs text-[var(--text-muted)] space-y-1">
          <p className="font-medium text-[var(--text)]">
            Provenance for Novacure Labs
          </p>
          <p className="text-[11px] text-[var(--text-muted)]">
            * Note: Minutes saved is an estimate based on average literature search times. In this demo, role is chosen via demo login; in production, role permissions are securely synchronized from enterprise SSO group claims.
          </p>
        </div>
      </footer>
    </div>
  );
}
