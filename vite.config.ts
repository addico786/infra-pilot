import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0", // Allow access from WSL and network
    port: 5173, // Default Vite port
    strictPort: false, // Allow port fallback if 5173 is taken
  },
});

