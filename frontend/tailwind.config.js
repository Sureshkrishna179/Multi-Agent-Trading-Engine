/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        mono: ['"JetBrains Mono"', 'Fira Code', 'Consolas', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        terminal: {
          bg:      '#080810',
          surface: '#0d0d1a',
          card:    '#111120',
          border:  '#1e1e2e',
          border2: '#2d2d3f',
          muted:   '#4b5563',
          dim:     '#374151',
          text:    '#e2e8f0',
          sub:     '#9ca3af',
        },
        bull:  '#22c55e',
        bear:  '#ef4444',
        hold:  '#6b7280',
        brand: '#7c3aed',
        warn:  '#f59e0b',
      },
      animation: {
        'pulse-bull': 'pulseBull 2s cubic-bezier(0.4,0,0.6,1) infinite',
        'pulse-bear': 'pulseBear 2s cubic-bezier(0.4,0,0.6,1) infinite',
        'slide-in':   'slideIn 0.3s ease-out',
        'fade-up':    'fadeUp 0.4s ease-out',
      },
      keyframes: {
        pulseBull: {
          '0%,100%': { boxShadow: '0 0 4px #22c55e88' },
          '50%':     { boxShadow: '0 0 12px #22c55ecc' },
        },
        pulseBear: {
          '0%,100%': { boxShadow: '0 0 4px #ef444488' },
          '50%':     { boxShadow: '0 0 12px #ef4444cc' },
        },
        slideIn: {
          from: { opacity: 0, transform: 'translateX(12px)' },
          to:   { opacity: 1, transform: 'translateX(0)' },
        },
        fadeUp: {
          from: { opacity: 0, transform: 'translateY(10px)' },
          to:   { opacity: 1, transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}

