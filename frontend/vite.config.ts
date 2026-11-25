import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, ".", "MATERA_");
  const httpsLocal = env.MATERA_HTTPS_DEV === "true";
  const httpsHost = env.MATERA_HTTPS_HOST || "localhost";

  return {
    plugins: [react()],
    server: {
      host: "127.0.0.1",
      strictPort: true,
      allowedHosts: httpsLocal ? [httpsHost, "localhost"] : undefined,
      hmr: httpsLocal
        ? {
            host: httpsHost,
            protocol: "wss",
            clientPort: 5443,
          }
        : undefined,
    },
  };
});
