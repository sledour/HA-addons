/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: { unoptimized: true },
  // Ne mets PAS de assetPrefix ou basePath pour l'instant, 
  // laissons Express gérer le service de fichiers.
}

module.exports = nextConfig