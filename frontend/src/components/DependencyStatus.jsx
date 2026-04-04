import React, { useState, useEffect } from 'react';
import { CheckCircle, AlertTriangle, XCircle, ChevronDown, ChevronUp, RefreshCw } from 'lucide-react';
import api from '../lib/api';

/**
 * DependencyStatus - 外部服務狀態指示器
 * ========================================
 * 嵌入側邊欄底部，顯示外部依賴（露天 API、Konami DB 等）的連線狀態。
 * 頁面載入時自動檢查一次，也可手動重新檢查。
 */
const DependencyStatus = () => {
    const [status, setStatus] = useState(null);     // { all_ok, results }
    const [loading, setLoading] = useState(true);
    const [expanded, setExpanded] = useState(false);
    const [error, setError] = useState(false);

    // ============================================================
    // 載入時自動檢查外部依賴
    // ============================================================
    useEffect(() => {
        checkDependencies();
    }, []);

    const checkDependencies = async () => {
        setLoading(true);
        setError(false);
        try {
            const res = await api.get('/health/dependencies');
            setStatus(res.data);
        } catch {
            setError(true);
        } finally {
            setLoading(false);
        }
    };

    // ============================================================
    // 渲染狀態指示器
    // ============================================================
    if (loading) {
        return (
            <div className="px-4 py-2 text-xs text-text-muted flex items-center gap-2">
                <RefreshCw size={12} className="animate-spin" />
                檢查外部服務...
            </div>
        );
    }

    if (error) {
        return (
            <div className="px-4 py-2">
                <button
                    onClick={checkDependencies}
                    className="flex items-center gap-2 text-xs text-danger hover:text-red-400 transition-colors"
                >
                    <XCircle size={12} />
                    無法檢查服務狀態（點擊重試）
                </button>
            </div>
        );
    }

    if (!status) return null;

    const failedCount = status.results.filter(r => !r.ok).length;

    return (
        <div className="px-4 py-2 border-t border-slate-700">
            {/* 摘要行（可展開） */}
            <button
                onClick={() => setExpanded(!expanded)}
                className="flex items-center justify-between w-full text-xs group"
            >
                <div className="flex items-center gap-2">
                    {status.all_ok ? (
                        <>
                            <span className="w-2 h-2 rounded-full bg-success animate-pulse" />
                            <span className="text-success">服務正常</span>
                        </>
                    ) : (
                        <>
                            <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
                            <span className="text-amber-400">
                                {failedCount} 項服務異常
                            </span>
                        </>
                    )}
                </div>
                <div className="flex items-center gap-1 text-text-muted">
                    <button
                        onClick={(e) => {
                            e.stopPropagation();
                            checkDependencies();
                        }}
                        className="p-0.5 hover:text-white transition-colors"
                        title="重新檢查"
                    >
                        <RefreshCw size={11} />
                    </button>
                    {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                </div>
            </button>

            {/* 展開的詳細列表 */}
            {expanded && (
                <div className="mt-2 space-y-1.5 animate-fadeIn">
                    {status.results.map((dep, i) => (
                        <div
                            key={i}
                            className="flex items-center gap-2 text-xs"
                        >
                            {dep.ok ? (
                                <CheckCircle size={12} className="text-success shrink-0" />
                            ) : (
                                <AlertTriangle size={12} className="text-amber-400 shrink-0" />
                            )}
                            <span className={dep.ok ? 'text-text-muted' : 'text-amber-400'}>
                                {dep.name}
                            </span>
                            {!dep.ok && dep.error && (
                                <span className="text-slate-500 ml-auto">
                                    {dep.error}
                                </span>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default DependencyStatus;
