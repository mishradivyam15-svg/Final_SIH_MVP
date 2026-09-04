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
        // Priority semantics
        priority: {
          high: '#b3261e',
          highBg: '#fdecea',
          highBorder: '#f3c2bd',
          medium: '#8a5a00',
          mediumBg: '#fdf3dc',
          mediumBorder: '#f0d9a0',
          low: '#1f6f4a',
          lowBg: '#e8f5ee',
          lowBorder: '#bfe3cf',
        },
        status: {
          open: '#28518b',
          openBg: '#eaf1fa',
          confirmed: '#b3261e',
          confirmedBg: '#fdecea',
          investigating: '#8a5a00',
          investigatingBg: '#fdf3dc',
          dismissed: '#5b6470',
          dismissedBg: '#eef0f2',
        },
        surface: {
          DEFAULT: '#ffffff',
          subtle: '#f7f8fa',
          muted: '#eef0f3',
        },
        ink: {
          900: '#12161c',
          700: '#333944',
          500: '#5b6470',
          400: '#7c8593',
          300: '#a4acb8',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      boxShadow: {
        card: '0 1px 2px 0 rgba(16, 27, 48, 0.06), 0 1px 3px 0 rgba(16, 27, 48, 0.08)',
        panel: '0 2px 8px 0 rgba(16, 27, 48, 0.08)',
      },
      borderRadius: {
        md: '8px',
        lg: '12px',
      },
    },
  },
  plugins: [],
}
