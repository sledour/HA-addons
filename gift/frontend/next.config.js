/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Supprime la vérification ESLint au build pour éviter les blocages HA
  eslint: {
    ignoreDuringBuilds: true,
  },
}

module.exports = nextConfig