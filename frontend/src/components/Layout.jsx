import React from 'react';
import { LayoutDashboard, ShoppingCart, Settings, Moon, Sun } from 'lucide-react';

const Layout = ({ children }) => {
    return (
        <div className="flex h-screen bg-background text-text">
            {/* Sidebar */}
            <aside className="w-64 bg-surface border-r border-slate-700 flex flex-col">
                <div className="p-6 border-b border-slate-700">
                    <h1 className="text-xl font-bold flex items-center gap-2 text-primary">
                        <span className="text-2xl">⚡</span> YGO Scraper
                    </h1>
                </div>

                <nav className="flex-1 p-4 space-y-2">
                    <NavItem icon={<LayoutDashboard size={20} />} label="專案列表" active />
                </nav>

                <div className="p-4 border-t border-slate-700 text-xs text-text-muted text-center">
                    v2.0.0 React Refactor
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-auto">
                <header className="h-16 bg-surface border-b border-slate-700 flex items-center justify-between px-8">
                    <h2 className="text-lg font-medium">控制台</h2>
                    <div className="flex gap-4">
                        {/* Placeholder for future header items */}
                    </div>
                </header>
                <div className="p-8">
                    {children}
                </div>
            </main>
        </div>
    );
};

const NavItem = ({ icon, label, active = false }) => {
    return (
        <div
            className={`flex items-center gap-3 px-4 py-3 rounded-lg cursor-pointer transition-colors ${active
                ? 'bg-primary/20 text-primary border border-primary/20'
                : 'text-text-muted hover:bg-slate-700/50 hover:text-white'
                }`}
        >
            {icon}
            <span className="font-medium">{label}</span>
        </div>
    );
};

export default Layout;
