/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    unoptimized: true,
  },
  trailingSlash: false,
  async rewrites() {
    const backendUrl = process.env.BACKEND_URL || 'https://api-handler-zkzefofekg.ap-southeast-1.fcapp.run';
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
      {
        source: '/health',
        destination: `${backendUrl}/health`,
      },
    ];
  },
}

module.exports = nextConfig
