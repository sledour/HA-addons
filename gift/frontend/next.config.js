/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  // Ajoute cette ligne pour que les liens ne commencent pas par "/" au sens strict du domaine
  assetPrefix: './', 
}

module.exports = nextConfig