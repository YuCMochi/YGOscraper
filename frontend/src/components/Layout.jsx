import React, { useState } from 'react';
import { LayoutDashboard, Settings, ChevronDown, ChevronUp } from 'lucide-react';
import GlobalSettingsPanel from './GlobalSettingsPanel';
import DependencyStatus from './DependencyStatus';

/**
 * Layout - 主版面配置
 * ====================
 * 包含左側欄（導航 + 全域設定 + 服務狀態）和主要內容區。
 * v0.3.0: 新增「全域設定」展開面板和底部「服務狀態」指示器。
 */
const Layout = ({ children }) => {
    // 控制全域設定面板的展開/收合
    const [settingsOpen, setSettingsOpen] = useState(false);

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

                    {/* 全域設定（展開/收合） */}
                    <div
                        onClick={() => setSettingsOpen(!settingsOpen)}
                        className={`flex items-center justify-between px-4 py-3 rounded-lg cursor-pointer transition-colors ${
                            settingsOpen
                                ? 'bg-primary/20 text-primary border border-primary/20'
                                : 'text-text-muted hover:bg-slate-700/50 hover:text-white'
                        }`}
                    >
                        <div className="flex items-center gap-3">
                            <Settings size={20} />
                            <span className="font-medium">全域設定</span>
                        </div>
                        {settingsOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                    </div>

                    {/* 全域設定面板 */}
                    <GlobalSettingsPanel
                        isOpen={settingsOpen}
                        onToggle={() => setSettingsOpen(!settingsOpen)}
                    />
                </nav>

                {/* 底部：服務狀態 + 版本號 */}
                <DependencyStatus />
                <div className="p-4 border-t border-slate-700 text-xs text-text-muted text-center">
                    v0.3.0
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
