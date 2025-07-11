/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
  // Add cache busting with timestamp
  generateBuildId: () => {
    return `build-${Date.now()}`;
  },
  // Add environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    BUILD_TIME: new Date().toISOString(),
  },
  // Configure export path mapping
  exportPathMap: async function (
    defaultPathMap,
    { dev, dir, outDir, distDir, buildId }
  ) {
    return {
      '/': { page: '/' },
    };
  },
  // Disable server-side features for static export
  poweredByHeader: false,
  compress: true,
};

export default nextConfig;
