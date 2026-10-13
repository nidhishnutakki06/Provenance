import React, { useState, useEffect } from 'react';
import { useRole } from './context/RoleContext';
import * as api from './api';
import Chat from './components/Chat';
import Onboarding from './components/Onboarding';
import Experts from './components/Experts';
import Dashboard from './components/Dashboard';

const ROLE_DESCRIPTIONS = {
  intern: 'Intern clearance: Authorized for standard SOPs and onboarding guides (7 docs). Restricted audit and CAPA records are hidden.',
  analyst: 'Analyst clearance: Authorized for technical operations, CAPAs, deviations, and SOPs (18 docs). Confidential executive audits excluded.',
  manager: 'Manager clearance: Full unrestricted enterprise visibility across all 20 documents, confidential audits (AUD-001), and executive emails.',
};

export default function App() {
  const { role, setRole } = useRole();
  const [activeTab, setActiveTab] = useState('chat'); // 'chat' | 'onboarding-experts' | 'dashboard'
  const [oeSubTab, setOeSubTab] = useState('onboarding'); // 'onboarding' | 'experts'
  const [health, setHealth] = useState(null);
  const [backendError, setBackendError] = useState(null);

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
          console.error("Health check failed:", err);
          setBackendError("Backend is unreachable at " + (import.meta.env.VITE_API_URL || "http://localhost:8000") + ". Please start the FastAPI server.");
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

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100">
      {/* Top Warning Banner if Backend Unreachable */}
      {backendError && (
        <div className="bg-rose-600 text-white px-4 py-2.5 text-center text-xs sm:text-sm font-medium flex items-center justify-center gap-2 shadow-inner">
          <svg className="w-4 h-4 shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          <span>{backendError}</span>
        </div>
      )}

      {/* Main Header */}
      <header className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 shadow-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            {/* Logo and Tagline */}
            <div>
              <div className="flex items-center gap-2.5">
                <span className="text-2xl">🛡️</span>
                <h1 className="text-xl sm:text-2xl font-black tracking-tight text-slate-950 dark:text-white">
                  Provenance
                </h1>
                <span className="text-[11px] px-2 py-0.5 rounded-full font-semibold bg-indigo-50 text-indigo-700 dark:bg-indigo-950/80 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
                  Pharma · Novacure Labs
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 font-medium italic">
                “Search tells you where. Provenance tells you whether to trust it.”
              </p>
            </div>

            {/* Role Switcher & Health Indicator */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
              {/* Health Dot */}
              <div className="flex items-center gap-2 px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 text-xs">
                <span className={`w-2 h-2 rounded-full ${health ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`} />
                <span className="text-[11px] font-mono text-slate-600 dark:text-slate-300">
                  {health
                    ? `LLM: ${health.llm} · Data: ${health.data_source} (${health.chunks || 46} chunks)`
                    : 'Backend Offline'}
                </span>
              </div>

              {/* Role Toggle */}
              <div className="flex items-center rounded-xl bg-slate-100 dark:bg-slate-800 p-1 border border-slate-200 dark:border-slate-700">
                {['intern', 'analyst', 'manager'].map((r) => (
                  <button
                    key={r}
                    type="button"
                    onClick={() => setRole(r)}
                    className={`px-3 py-1 text-xs font-semibold rounded-lg capitalize transition ${
                      role === r
                        ? 'bg-white dark:bg-indigo-600 text-slate-900 dark:text-white shadow-sm'
                        : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                    }`}
                  >
                    {r}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Role Clearance Description Banner */}
          <div className="mt-2.5 pt-2 border-t border-slate-100 dark:border-slate-800/80 text-[11px] text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
            <span className="font-semibold text-slate-700 dark:text-slate-300">Security Clearance:</span>
            <span>{ROLE_DESCRIPTIONS[role] || ''}</span>
          </div>
        </div>

        {/* Tab Navigation (No Router) */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 border-t border-slate-200 dark:border-slate-800">
          <nav className="flex space-x-6">
            <button
              onClick={() => setActiveTab('chat')}
              className={`py-3 px-1 text-sm font-semibold border-b-2 transition ${
                activeTab === 'chat'
                  ? 'border-indigo-600 text-indigo-600 dark:text-indigo-400'
                  : 'border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200'
              }`}
            >
              💬 Enterprise Chat
            </button>
            <button
              onClick={() => setActiveTab('onboarding-experts')}
              className={`py-3 px-1 text-sm font-semibold border-b-2 transition ${
                activeTab === 'onboarding-experts'
                  ? 'border-indigo-600 text-indigo-600 dark:text-indigo-400'
                  : 'border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200'
              }`}
            >
              📚 Onboarding and Experts
            </button>
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`py-3 px-1 text-sm font-semibold border-b-2 transition ${
                activeTab === 'dashboard'
                  ? 'border-indigo-600 text-indigo-600 dark:text-indigo-400'
                  : 'border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200'
              }`}
            >
              📊 Intelligence Dashboard
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto pb-16">
        {activeTab === 'chat' && (
          <Chat key={`chat-${role}`} />
        )}

        {activeTab === 'onboarding-experts' && (
          <div className="py-4 space-y-4">
            {/* Subtab toggle */}
            <div className="max-w-4xl mx-auto px-4 flex gap-2">
              <button
                onClick={() => setOeSubTab('onboarding')}
                className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition ${
                  oeSubTab === 'onboarding'
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'bg-slate-200 text-slate-700 dark:bg-slate-800 dark:text-slate-300'
                }`}
              >
                Curated Onboarding Paths
              </button>
              <button
                onClick={() => setOeSubTab('experts')}
                className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition ${
                  oeSubTab === 'experts'
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'bg-slate-200 text-slate-700 dark:bg-slate-800 dark:text-slate-300'
                }`}
              >
                Subject Matter Experts
              </button>
            </div>

            {oeSubTab === 'onboarding' ? (
              <Onboarding key={`onboarding-${role}`} />
            ) : (
              <Experts key={`experts-${role}`} />
            )}
          </div>
        )}

        {activeTab === 'dashboard' && (
          <Dashboard key={`dashboard-${role}`} />
        )}
      </main>

      {/* Footer */}
      <footer className="mt-auto border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 py-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-xs text-slate-500 dark:text-slate-400 space-y-1">
          <p>
            Provenance Enterprise Knowledge Assistant · Novacure Labs
          </p>
          <p className="text-[11px] text-slate-400 dark:text-slate-500">
            * Note: Minutes saved is an estimate based on average literature search times. In this demo, role is chosen via the UI header; in production, role permissions are securely synchronized from enterprise SSO group claims.
          </p>
        </div>
      </footer>
    </div>
  );
}
