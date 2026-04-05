import React, { useState, useEffect } from 'react';
import { LayoutDashboard, Settings } from 'lucide-react';
import GlobalSettingsModal from './GlobalSettingsModal';
import DependencyStatus from './DependencyStatus';

/**
 * Layout - 主版面配置
 * ====================
 * 包含左側欄（導航 + 服務狀態）和主要內容區。
 * v0.3.0: 全域設定從側邊欄移至右上角 Modal。
 * v0.4.1: 版本號改為從 GET /api/version 動態讀取。
 */
const Layout = ({ children }) => {
    const [settingsOpen, setSettingsOpen] = useState(false);
    const [appVersion, setAppVersion] = useState(null);

    useEffect(() => {
        fetch('/api/version')
            .then((res) => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return res.json();
            })
            .then((data) => setAppVersion(data.version ?? null))
            .catch(() => setAppVersion(null));
    }, []);

    return (
        <div className="flex h-screen bg-background text-text">
            {/* Sidebar */}
            <aside className="w-64 bg-surface border-r border-slate-700 flex flex-col">
                {/* Logo */}
                <div className="p-6 border-b border-slate-700">
                    <h1 className="text-xl font-bold flex items-center gap-2 text-primary">
                        <span className="text-2xl">⚡</span> YGO Scraper
                    </h1>
                </div>

                {/* 導航區 */}
                <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
                    <NavItem icon={<LayoutDashboard size={20} />} label="專案列表" active />
                </nav>

                {/* 底部：服務狀態 + 版本號 */}
                <DependencyStatus />
                <div className="p-4 border-t border-slate-700 text-xs text-text-muted text-center">
                    {appVersion != null ? `v${appVersion}` : '—'}
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-auto">
                <header className="h-16 bg-surface border-b border-slate-700 flex items-center justify-between px-8">
                    <h2 className="text-lg font-medium">控制台</h2>
                    <div className="flex gap-4">
                        {/* 全域設定按鈕 */}
                        <button
                            onClick={() => setSettingsOpen(true)}
                            className="p-2 rounded-lg text-text-muted hover:text-white hover:bg-slate-700 transition-colors"
                            title="全域設定"
                        >
                            <Settings size={20} />
                        </button>
                    </div>
                </header>
                <div className="p-8">
                    {children}
                </div>
            </main>

            {/* 全域設定 Modal */}
            <GlobalSettingsModal
                isOpen={settingsOpen}
                onClose={() => setSettingsOpen(false)}
            />
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
