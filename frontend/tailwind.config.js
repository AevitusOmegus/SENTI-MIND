/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      colors: {
        sage: {
          100: "#F1F8E9",
          200: "#DCEDC8",
          300: "#A5D6A7",
          400: "#81C784",
          500: "#4CAF50",
          700: "#2E7D32",
          800: "#1B5E20",
        },
        cloud: {
          100: "#E1F5FE",
          200: "#B3E5FC",
          300: "#81D4FA",
        },
        indigo: {
          300: "#7986CB",
          400: "#5C6BC0",
        },
        amber: {
          300: "#FFD54F",
          400: "#FFCA28",
        },
        rose: {
          300: "#F06292",
          400: "#E57373",
          500: "#EF5350",
        },
      },
      backdropBlur: {
        xs: "2px",
      },
      boxShadow: {
        glass: "0 8px 32px rgba(46, 125, 50, 0.12)",
        "glass-lg": "0 16px 48px rgba(46, 125, 50, 0.16)",
        card: "0 4px 24px rgba(0, 0, 0, 0.06)",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "fade-in": "fadeIn 0.4s ease-out",
        "slide-up": "slideUp 0.4s ease-out",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: 0 },
          "100%": { opacity: 1 },
        },
        slideUp: {
          "0%": { opacity: 0, transform: "translateY(16px)" },
          "100%": { opacity: 1, transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
};
