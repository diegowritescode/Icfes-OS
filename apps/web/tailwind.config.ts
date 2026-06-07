import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#172026",
        panel: "#f8faf9",
        line: "#d9e2df"
      },
      boxShadow: {
        soft: "0 8px 30px rgba(23, 32, 38, 0.07)"
      }
    }
  },
  plugins: []
};

export default config;
