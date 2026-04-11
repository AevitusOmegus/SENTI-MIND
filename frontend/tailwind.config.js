/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      colors: {
        // Primary Sage Green - Medical, Calming, Accessible
        primary: {
          50: "#f4f7f4",
          100: "#e8f0e8",
          200: "#c5d8c5",
          300: "#9cb89c",
          400: "#729672",
          500: "#5a7c5a", // Sage Green - Main primary
          600: "#4a654a",
          700: "#3d523d",
          800: "#314131",
          900: "#293629",
        },
        // Clinical Colors - Color-blind friendly & WCAG compliant
        clinical: {
          calm: "#6b9080",     // Sage for normal states
          caution: "#c4a35a",  // Muted gold for stress
          concern: "#b88a6f",  // Warm terracotta for anxiety
          warning: "#c17a5c",  // Soft rust for depression
          critical: "#b85450", // Muted red for suicidal (emergency)
        },
        // Sage Green Ecosystem
        sage: {
          50: "#f6f8f6",
          100: "#e8efe8",
          200: "#d1e0d1",
          300: "#b0cbb0",
          400: "#84a884",
          500: "#648a64",
          600: "#4d6e4d",
          700: "#3e573e",
          800: "#334633",
          900: "#2b3a2b",
        },
        // Neutral Warm Grays - Reduce eye strain
        warm: {
          50: "#fafaf9",
          100: "#f5f5f4",
          200: "#e7e5e4",
          300: "#d6d3d1",
          400: "#a8a29e",
          500: "#78716c",
          600: "#57534e",
          700: "#44403c",
          800: "#292524",
          900: "#1c1917",
        },
        // Medical Semantic Colors
        medical: {
          safe: "#5a7c5a",      // Sage green - safe/normal
          mild: "#d4a574",      // Soft amber - mild concern
          moderate: "#c9916b",  // Terracotta - moderate
          severe: "#b87068",    // Rose-terracotta - severe
          emergency: "#a94442", // Accessible red - emergency
        },
        // Legacy compatibility
        cloud: {
          100: "#E1F5FE",
          200: "#B3E5FC",
          300: "#81D4FA",
        },
      },
      backgroundImage: {
        'dashboard-texture': "url('/dashboard-texture.png')",
      },
      backdropBlur: {
        xs: "2px",
      },
      boxShadow: {
        // Soft, medical-grade shadows
        medical: "0 2px 8px rgba(90, 124, 90, 0.08)",
        "medical-md": "0 4px 16px rgba(90, 124, 90, 0.12)",
        "medical-lg": "0 8px 32px rgba(90, 124, 90, 0.15)",
        // Legacy
        glass: "0 4px 16px rgba(15, 23, 42, 0.05)",
        "glass-lg": "0 8px 32px rgba(15, 23, 42, 0.08)",
        card: "0 2px 12px rgba(15, 23, 42, 0.04)",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "breathe": "breathe 4s ease-in-out infinite",
        "fade-in": "fadeIn 0.4s ease-out",
        "slide-up": "slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1)",
        "slide-down": "slideDown 0.4s cubic-bezier(0.16, 1, 0.3, 1)",
        "gentle-pulse": "gentlePulse 3s ease-in-out infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: 0 },
          "100%": { opacity: 1 },
        },
        slideUp: {
          "0%": { opacity: 0, transform: "translateY(20px)" },
          "100%": { opacity: 1, transform: "translateY(0)" },
        },
        slideDown: {
          "0%": { opacity: 0, transform: "translateY(-10px)" },
          "100%": { opacity: 1, transform: "translateY(0)" },
        },
        breathe: {
          "0%, 100%": { transform: "scale(1)", opacity: 1 },
          "50%": { transform: "scale(1.02)", opacity: 0.8 },
        },
        gentlePulse: {
          "0%, 100%": { opacity: 1 },
          "50%": { opacity: 0.7 },
        },
      },
    },
  },
  plugins: [],
};
