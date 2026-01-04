/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true, // Aide Express à trouver les dossiers
  images: { unoptimized: true }, // Obligatoire pour l'export statique sur HA
}

module.exports = nextConfig