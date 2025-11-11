/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      animation: {
        'float': 'float 2s ease-in-out forwards',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        float: {
          '0%': { 
            transform: 'translateY(0) scale(1)',
            opacity: '1'
          },
          '100%': { 
            transform: 'translateY(-500px) scale(1.5)',
            opacity: '0'
          }
        }
      }
    },
  },
  plugins: [],
}
