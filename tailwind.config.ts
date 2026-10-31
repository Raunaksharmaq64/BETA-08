import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        graphite: {
          900: "#181a1f",
          800: "#1a1c21",
          700: "#23262d",
        },
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "system-ui", "sans-serif"],
        mono: ["Liberation Mono", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      boxShadow: {
        glass: "0px 25px 50px -12px rgba(0, 0, 0, 0.25)",
        pill: "0px 16px 32px -4px rgba(24, 26, 31, 0.28)",
        soft: "0px 2px 10px 0px rgba(0, 0, 0, 0.02)",
      },
    },
  },
  plugins: [],
};
export default config;

