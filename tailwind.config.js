/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Neutral / brand
        brand: {
          50: '#f0f5fb',
          100: '#dae6f4',
          200: '#b3cce9',
          300: '#82abd9',
          400: '#5486c4',
          500: '#3568ab',
          600: '#28518b',
          700: '#213f6d',
          800: '#1d3459',
          900: '#1a2c4a',
          950: '#101b30',
        },
        // Priority semantics — tuned for a dark control-room surface:
        // saturated enough to read as an alert, dark-tinted backgrounds
        // instead of light pastels.
        priority: {
          high: '#f87171',
          highBg: '#3a1416',
          highBorder: '#7f2f31',
          medium: '#fbbf24',
          mediumBg: '#362808',
          mediumBorder: '#7a5c17',
          low: '#4ade80',
          lowBg: '#122a1c',
          lowBorder: '#2c6a45',
        },
        status: {
          open: '#7aa8d9',
          openBg: '#122236',
          confirmed: '#f87171',
          confirmedBg: '#3a1416',
          investigating: '#fbbf24',
          investigatingBg: '#362808',
          dismissed: '#9aa2ad',
          dismissedBg: '#1e232b',
        },
        // Dark, tinted-navy surfaces — card bg sits a step lighter than
        // page bg so elevation still reads without relying on shadows.
        surface: {
          DEFAULT: '#151a23',
          subtle: '#0b0e14',
          muted: '#1e2530',
        },
        // Same key semantics as before (900 = strongest emphasis, 300 =
        // faintest) but with lightness inverted for light-text-on-dark.
        ink: {
          900: '#eef1f5',
          700: '#b7c0cc',
          500: '#8a93a1',
          400: '#666f7c',
          300: '#333a44',
        },
      },
      fontFamily: {
        sans: ['Outfit', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      boxShadow: {
        // Dark surfaces: a subtle light inner edge (glassmorphism) reads
        // as elevation better than a shadow, which barely shows on dark.
        card: '0 0 0 1px rgba(255, 255, 255, 0.045), 0 2px 10px 0 rgba(0, 0, 0, 0.35)',
        panel: '0 0 0 1px rgba(255, 255, 255, 0.06), 0 12px 32px -8px rgba(0, 0, 0, 0.55)',
        glow: '0 0 0 1px rgba(122, 168, 217, 0.18), 0 8px 28px -6px rgba(53, 104, 171, 0.45)',
      },
      borderRadius: {
        md: '8px',
        lg: '12px',
        xl: '16px',
      },
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '150% 0' },
          '100%': { backgroundPosition: '-150% 0' },
        },
        'fade-in-up': {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'grow-x': {
          '0%': { transform: 'scaleX(0)' },
          '100%': { transform: 'scaleX(1)' },
        },
        sweep: {
          '0%': { backgroundPosition: '200% 0' },
          '100%': { backgroundPosition: '-200% 0' },
        },
        'pulse-glow': {
          '0%, 100%': { opacity: '0.5' },
          '50%': { opacity: '1' },
        },
        'pulse-ring': {
          '0%': { transform: 'scale(0.8)', opacity: '0.6' },
          '70%, 100%': { transform: 'scale(2.4)', opacity: '0' },
        },
        breathe: {
          '0%, 100%': { opacity: '0.75', transform: 'scale(1)' },
          '50%': { opacity: '1', transform: 'scale(1.06)' },
        },
      },
      animation: {
        shimmer: 'shimmer 1.8s ease-in-out infinite',
        'fade-in-up': 'fade-in-up 0.5s cubic-bezier(0.16, 1, 0.3, 1) both',
        'fade-in': 'fade-in 0.4s ease-out both',
        'grow-x': 'grow-x 0.6s cubic-bezier(0.16, 1, 0.3, 1) both',
        sweep: 'sweep 3s ease-in-out infinite',
        'pulse-glow': 'pulse-glow 3.2s ease-in-out infinite',
        'pulse-ring': 'pulse-ring 2.4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        breathe: 'breathe 3.5s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
