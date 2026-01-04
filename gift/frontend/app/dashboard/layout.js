'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import './dashboard.css';

export default function DashboardLayout({ children }) {
    const pathname = usePathname();

    // Fonction pour savoir si l'onglet est actif
    const isActive = (path) => pathname.includes(path);

    return (
        <div className="dashboard-wrapper">
            <main className="dashboard-container">
                {children}
            </main>

            <nav className="bottom-nav">
                <Link href="/dashboard/" className={`nav-item ${pathname === '/dashboard/' ? 'active' : ''}`}>
                    <span className="nav-icon">🎁</span>
                    <span>Ma Liste</span>
                </Link>
                <Link href="/dashboard/events/" className={`nav-item ${isActive('events') ? 'active' : ''}`}>
                    <span className="nav-icon">📅</span>
                    <span>Événements</span>
                </Link>
                <Link href="/dashboard/settings/" className={`nav-item ${isActive('settings') ? 'active' : ''}`}>
                    <span className="nav-icon">⚙️</span>
                    <span>Réglages</span>
                </Link>
            </nav>
        </div>
    );
}