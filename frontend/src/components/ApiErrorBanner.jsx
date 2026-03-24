/**
 * ApiErrorBanner.jsx - 共用 API 錯誤提示元件
 * =============================================
 * 在頁面頂部顯示可關閉的錯誤橫幅，支援不同等級：
 * - 網路斷線（紅底，帶重新連線提示）
 * - 後端錯誤（橘底，帶錯誤詳情）
 * - 一般訊息（灰底）
 *
 * Props:
 *   error   {string|object} - 錯誤訊息或 axios error 物件
 *   onDismiss {function}    - 關閉時的回呼函式（若不傳則不顯示關閉鈕）
 *   className {string}      - 額外的 CSS 類別
 */
import React from 'react';
import { AlertCircle, WifiOff, X } from 'lucide-react';

/**
 * 判斷錯誤類型，回傳統一的 { type, message } 物件
 *  - type: 'network' | 'server' | 'general'
 *  - message: 使用者友善的錯誤訊息
 */
const classifyError = (error) => {
    // 已經是字串，當作一般錯誤
    if (typeof error === 'string') {
        return { type: 'general', message: error };
    }

    // axios error 物件
    if (error?.isAxiosError || error?.response || error?.request) {
        // 沒有收到 response → 網路斷線或後端沒開
        if (!error.response) {
            return {
                type: 'network',
                message: '無法連線到伺服器，請確認後端是否正在運作。',
            };
        }

        // 有收到 response → 後端回報錯誤
        const status = error.response.status;
        const detail = error.response.data?.detail || '';

        if (status >= 500) {
            return {
                type: 'server',
                message: detail || `伺服器內部錯誤 (${status})`,
            };
        }

        if (status === 404) {
            return {
                type: 'general',
                message: detail || '找不到請求的資源 (404)',
            };
        }

        return {
            type: 'general',
            message: detail || `請求失敗 (${status})`,
        };
    }

    // 其他 Error 物件
    if (error?.message) {
        return { type: 'general', message: error.message };
    }

    return { type: 'general', message: '發生未知錯誤' };
};

// 不同類型對應的樣式
const STYLES = {
    network: {
        bg: 'bg-red-900/30 border-red-500/40',
        icon: <WifiOff size={20} className="text-red-400 flex-shrink-0" />,
        textColor: 'text-red-200',
    },
    server: {
        bg: 'bg-amber-900/30 border-amber-500/40',
        icon: <AlertCircle size={20} className="text-amber-400 flex-shrink-0" />,
        textColor: 'text-amber-200',
    },
    general: {
        bg: 'bg-slate-800 border-slate-600',
        icon: <AlertCircle size={20} className="text-slate-400 flex-shrink-0" />,
        textColor: 'text-slate-200',
    },
};

const ApiErrorBanner = ({ error, onDismiss, className = '' }) => {
    if (!error) return null;

    const { type, message } = classifyError(error);
    const style = STYLES[type];

    return (
        <div className={`flex items-start gap-3 p-4 rounded-xl border ${style.bg} ${className}`}>
            {style.icon}
            <p className={`flex-1 text-sm ${style.textColor}`}>{message}</p>
            {onDismiss && (
                <button
                    onClick={onDismiss}
                    className="text-slate-500 hover:text-white transition-colors flex-shrink-0 p-0.5"
                    aria-label="關閉錯誤訊息"
                >
                    <X size={16} />
                </button>
            )}
        </div>
    );
};

export default ApiErrorBanner;
