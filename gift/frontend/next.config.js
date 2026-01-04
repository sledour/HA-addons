/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: { unoptimized: true },
  // Force Next.js à ne jamais utiliser de "/" au début des liens
  assetPrefix: './', 
}
module.exports = nextConfig