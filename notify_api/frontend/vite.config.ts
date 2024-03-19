import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

// https://vitejs.dev/config/
export default defineConfig({
  base: "/api/plugins/notifyapi/frontend",
  plugins: [react()],
  server: {
    proxy: {
      "^/api/(?!plugins/notifyapi/frontend/).*": {
        target: "http://127.0.0.1:1329",
        secure: false,
        changeOrigin: true,
      },
    },
  },
});
