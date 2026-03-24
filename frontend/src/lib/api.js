/**
 * api.js - Axios 實例 + 統一錯誤攔截器
 * ======================================
 * 所有前端 API 呼叫都透過這個實例，確保：
 * 1. baseURL 統一指向 FastAPI 後端
 * 2. 錯誤會自動分類（方便 ApiErrorBanner 辨識網路斷線 vs 後端錯誤）
 */
import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000/api', // FastAPI server URL
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 300000, // 5 分鐘（爬蟲可能跑很久）
});

// ============================================================
// Response Interceptor：統一標記錯誤類型
// ============================================================
api.interceptors.response.use(
    // 成功的 response 直接 pass-through
    (response) => response,

    // 失敗時，在 error 物件上附加 isAxiosError 標記，方便下游辨識
    (error) => {
        // axios 本身已有 isAxiosError 屬性，這裡做額外標記
        if (!error.response) {
            // 沒有收到 response = 網路斷線 / 後端沒開 / 請求超時
            error._errorType = 'NETWORK_ERROR';
        } else if (error.response.status >= 500) {
            error._errorType = 'SERVER_ERROR';
        } else {
            error._errorType = 'CLIENT_ERROR';
        }
        return Promise.reject(error);
    }
);

export default api;
