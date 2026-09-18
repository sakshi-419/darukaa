/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        forest: {
          50: "#f2f8f4",
          100: "#e1efe4",
          200: "#c4decb",
          300: "#99c4a5",
          400: "#6aa57c",
          500: "#49885c",
          600: "#366d48",
          700: "#2d573b",
          800: "#274632",
          900: "#1e3727",
          950: "#0e1e15",
        },
        earth: {
          50: "#f8f6f0",
          100: "#f0ecd9",
          200: "#e0d7b3",
          300: "#ccbe88",
          400: "#b9a463",
          500: "#a58d4a",
          600: "#89713b",
          700: "#6e5732",
          800: "#5a462c",
          900: "#4b3b28",
          950: "#2a1f14",
        },
        biome: {
          dark: "#0b140f",
          card: "#122018",
          border: "#1d3326",
          accent: "#22c55e",
        }
      },
    },
  },
  plugins: [],
}
