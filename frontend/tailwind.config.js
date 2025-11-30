/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        espresso: "#0f0b0a",   // dark background
        roast: "#1c1514",      // sidebar background
        mocha: "#2a1f1d",      // chat panel variant
        foam: "#3b2e2c",       // message bubbles
        caramel: "#d5a16a",    // buttons
        gold: "#b38b59",       // hover/enhanced accent
        cream: "#f2e9e4",      // primary text
        latte: "#c7b8b2",      // secondary text
      },
    },
  },
  plugins: [],
};
