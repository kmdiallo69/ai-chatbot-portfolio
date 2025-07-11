/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
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
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://chatbot-backend-1752247339.livelyplant-d44fb3c4.eastus.azurecontainerapps.io',
    BUILD_TIME: new Date().toISOString(),
  },
  // Disable server-side features for static hosting
  poweredByHeader: false,
  compress: true,
};

export default nextConfig;
