import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        earth: {
          dark: '#0a0f0a',
          panel: '#111811',
          card: '#1a2e1a',
          border: '#2d4a2d',
          accent: '#4a7c59',
          light: '#8fb996',
          text: '#c8d8c8',
        }
      },
    },
  },
  plugins: [],
};
export default config;
