import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          light: "#6366f1",
          dark: "#818cf8",
          DEFAULT: "#6366f1",
        },
        secondary: {
          light: "#8b5cf6",
          dark: "#a78bfa",
          DEFAULT: "#8b5cf6",
        },
        accent: {
          light: "#ec4899",
          dark: "#f472b6",
          DEFAULT: "#ec4899",
        },
      },
      fontFamily: {
        sans: ["var(--font-geist-sans)", "Inter", "sans-serif"],
        mono: ["var(--font-geist-mono)", "JetBrains Mono", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;

