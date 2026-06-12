/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        bg: "var(--bg)",
        surface: "var(--surface)",
        "surface-raised": "var(--surface-raised)",
        accent: "var(--accent)",
        "accent-dim": "var(--accent-dim)",
        "accent-muted": "var(--accent-muted)",
        "text-primary": "var(--text-primary)",
        "text-muted": "var(--text-muted)",
        "ai-bg": "var(--ai-bg)",
        "ai-text": "var(--ai-text)",
        "citations-bg": "var(--citations-bg)",
        "citations-accent": "var(--citations-accent)",
      },
    },
  },
  plugins: [],
};
