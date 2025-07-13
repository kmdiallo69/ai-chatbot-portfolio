/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  trailingSlash: true,
  output: 'export',
  images: {
    unoptimized: true,
  },
  // Add cache busting with timestamp
  generateBuildId: () => {
    return `build-${Date.now()}`;
  },
  // Add environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://chatbot-backend-1752416081.whitebeach-62d10d97.southcentralus.azurecontainerapps.io',
    BUILD_TIME: new Date().toISOString(),
  },
  // Disable server-side features for static hosting
  poweredByHeader: false,
  compress: true,
};

export default nextConfig;
