/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        bg: 'var(--bg)',
        surface: {
          DEFAULT: 'var(--surface)',
          2: 'var(--surface-2)',
        },
        border: 'var(--border)',
        text: {
          DEFAULT: 'var(--text)',
          muted: 'var(--text-muted)',
        },
        accent: {
          DEFAULT: 'var(--accent)',
          hover: 'var(--accent-hover)',
          soft: 'var(--accent-soft)',
        },
        glow: {
          teal: 'var(--glow-teal)',
          blue: 'var(--glow-blue)',
        },
        danger: {
          soft: 'var(--danger-soft)',
          border: 'var(--danger-border)',
          text: 'var(--danger-text)',
        },
        success: {
          soft: 'var(--success-soft)',
          border: 'var(--success-border)',
          text: 'var(--success-text)',
        },
        violet: {
          soft: 'var(--violet-soft)',
          text: 'var(--violet-text)',
        },
        semantic: {
          success: 'var(--success)',
          warning: 'var(--warning)',
          danger: 'var(--danger)',
          neutral: 'var(--neutral)',
        },
      },
      fontFamily: {
        display: ['var(--font-display)'],
        sans: ['var(--font-sans)'],
        mono: ['var(--font-mono)'],
      },
      boxShadow: {
        'soft-sm': '0 1px 3px rgba(20, 32, 43, 0.04), 0 1px 2px rgba(20, 32, 43, 0.02)',
        'soft-md': '0 4px 12px rgba(20, 32, 43, 0.05), 0 1px 3px rgba(20, 32, 43, 0.03)',
        'soft-lg': '0 12px 32px rgba(20, 32, 43, 0.08), 0 2px 6px rgba(20, 32, 43, 0.04)',
      },
      borderRadius: {
        'card': '16px',
        'control': '12px',
        'pill': '9999px',
      },
      zIndex: {
        'header': '40',
        'backdrop': '60',
        'panel': '70',
        'toast': '80',
      },
    },
  },
  plugins: [],
}
