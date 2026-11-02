/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          950: '#060a12',
          900: '#0a0f1d',
          850: '#0e1626',
          800: '#131e33',
          700: '#1e2c4a',
          600: '#2d3f66',
        },
        cyber: {
          blue: '#3b82f6',
          cyan: '#06b6d4',
          teal: '#14b8a6',
        },
        traffic: {
          benign: '#10b981', // Emerald green
          attack: '#ef4444', // Red
          warning: '#f59e0b',
        }
      }
    },
  },
  plugins: [],
}
