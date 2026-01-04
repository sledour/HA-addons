/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true, 
  distDir: 'out',
  // On empêche Next.js de croire qu'il est à la racine du domaine
  images: { unoptimized: true },
}

module.exports = nextConfig