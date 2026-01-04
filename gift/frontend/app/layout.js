import './globals.css';

export const metadata = {
  title: 'Gift App - Liste de Cadeaux',
  description: 'Gérez vos listes de cadeaux collaborativement',
};

export default function RootLayout({ children }) {
  return (
    <html lang="fr">
      <body>
        {/* Le prop "children" représente la page actuelle (Login, Register, etc.) */}
        <main>{children}</main>
      </body>
    </html>
  );
}