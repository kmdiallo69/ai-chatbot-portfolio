/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  trailingSlash: true,
  // Required for Azure Static Web Apps deployment
  // The warning about API routes is expected since we use a separate backend
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
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://chatbot-backend.kindwater-a13bf119.westus.azurecontainerapps.io',
    BUILD_TIME: new Date().toISOString(),
  },
  // Optimizations for static hosting
  poweredByHeader: false,
  compress: true,
};

export default nextConfig;
