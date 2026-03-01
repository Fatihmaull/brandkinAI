/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  distDir: 'dist',
  images: {
    unoptimized: true,
  },
  trailingSlash: true,
  env: {
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || 'https://api.brandkin.ai',
    NEXT_PUBLIC_WEBSOCKET_URL: process.env.NEXT_PUBLIC_WEBSOCKET_URL || 'wss://ws.brandkin.ai',
    NEXT_PUBLIC_APP_KEY: process.env.NEXT_PUBLIC_APP_KEY || '',
    NEXT_PUBLIC_APP_SECRET: process.env.NEXT_PUBLIC_APP_SECRET || '',
  },
}

module.exports = nextConfig
