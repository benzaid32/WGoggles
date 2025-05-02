/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['localhost', '51.20.114.21'],
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://16.16.65.102:5000/:path*' // Pointing to EC2 instance
      }
    ]
  },
  async headers() {
    return [
      {
        // Apply these headers to all routes
        source: '/:path*',
        headers: [
          {
            key: 'Permissions-Policy',
            value: 'camera=*, microphone=*' // Allow camera and microphone access
          },
          {
            key: 'Cross-Origin-Embedder-Policy',
            value: 'require-corp'
          },
          {
            key: 'Cross-Origin-Opener-Policy',
            value: 'same-origin'
          }
        ]
      }
    ]
  }
}

export default nextConfig
