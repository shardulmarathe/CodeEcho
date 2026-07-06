import type { NextConfig } from "next";

const backendUrl =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000";

const nextConfig: NextConfig = {
  // Hide the dev-tools indicator so it can't appear in the build-time OG screenshot.
  devIndicators: false,
  async rewrites() {
    if (backendUrl.includes("localhost")) return [];
    return [{ source: "/api/:path*", destination: `${backendUrl}/api/:path*` }];
  },
};

export default nextConfig;
