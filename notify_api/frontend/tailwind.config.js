/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  daisyui: {
    themes: [
      "light",
      {
        dark: {
          primary: "#570DF8",
          secondary: "#F000B8",
          accent: "#37CDBE",
          neutral: "#3D4451",
          "base-100": "#222",
          info: "#3ABFF8",
          success: "#36D399",
          warning: "#FBBD23",
          error: "#F87272",
        },
      },
    ],
  },
  theme: {
    extend: {
      colors: {
        buttomBackgroundColor: 'rgb(79, 110, 211)',
        buttomHoverBackgroundColor: 'rgb(59, 78, 143)'
      }
    }
  },
  plugins: [require("daisyui"), require("tailwindcss-animated")],
};
