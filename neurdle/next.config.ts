import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  output: 'export',       // Static HTML export for Netlify
  trailingSlash: true,    // Clean URLs on static hosts
  images: {
    unoptimized: true,    // Required for static export
  },
};

export default nextConfig;
