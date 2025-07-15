// Configuration file to centralize environment variable access
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const BUILD_TIME = process.env.BUILD_TIME || new Date().toISOString();
const VERSION = '2025-01-11-v5-markdown-support';
const DEPLOYMENT = 'Azure Static Web Apps';

const config = {
    API_URL,
    BUILD_TIME,
    VERSION,
    DEPLOYMENT
};

export default config; 