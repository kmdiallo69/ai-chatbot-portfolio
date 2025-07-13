/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  trailingSlash: true,
  output: 'export',
  images: {
    unoptimized: true,
  },
  // Disable SSR for static export
  experimental: {
    esmExternals: false,
  },
  // Add cache busting with timestamp
  generateBuildId: () => {
    return `build-auth-fix-${Date.now()}`;
  },
  // Add environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://chatbot-backend.kindmushroom-11a9e276.westus.azurecontainerapps.io',
    BUILD_TIME: new Date().toISOString(),
  },
  // Disable server-side features for static hosting
  poweredByHeader: false,
  compress: true,
};

export default nextConfig;
