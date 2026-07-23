import type { NextConfig } from "next";

// GitHub project Pages needs "/iloilojobs". Vercel / custom domain: leave unset.
const basePath = process.env.BASE_PATH?.replace(/\/$/, "") || "";

const nextConfig: NextConfig = {
  output: "export",
  ...(basePath
    ? {
        basePath,
        assetPrefix: basePath,
      }
    : {}),
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
