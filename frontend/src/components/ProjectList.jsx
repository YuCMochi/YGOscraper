import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../lib/api';
import { FolderPlus, FolderOpen, Loader2 } from 'lucide-react';
import ApiErrorBanner from './ApiErrorBanner';

const ProjectList = () => {
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [creating, setCreating] = useState(false);
    const [error, setError] = useState(null);

    const fetchProjects = async () => {
        try {
            const res = await api.get('/projects');
            setProjects(res.data);
            setError(null);
        } catch (err) {
            console.error("Failed to fetch projects", err);
            setError(err);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateProject = async () => {
        setCreating(true);
        try {
            await api.post('/projects');
            await fetchProjects();
        } catch (err) {
            console.error("Failed to create project", err);
            setError(err);
        } finally {
            setCreating(false);
        }
    }

    useEffect(() => {
        fetchProjects();
    }, []);

    if (loading) {
        return (
            <div className="flex h-64 items-center justify-center text-text-muted">
                <Loader2 className="animate-spin mr-2" /> 正在載入專案...
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* API 錯誤提示 */}
            <ApiErrorBanner error={error} onDismiss={() => setError(null)} />
            <div className="flex justify-between items-center">
                <div>
                    <h3 className="text-2xl font-bold text-white">我的專案</h3>
                    <p className="text-text-muted">管理你的卡片採購清單</p>
                </div>
                <button
                    onClick={handleCreateProject}
                    disabled={creating}
                    className="flex items-center gap-2 bg-primary hover:bg-primary-hover text-white px-4 py-2 rounded-md font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {creating ? <Loader2 className="animate-spin" size={20} /> : <FolderPlus size={20} />}
                    新建專案
                </button>
            </div>

            {projects.length === 0 ? (
                <div className="bg-surface border border-slate-700 rounded-xl p-12 text-center">
                    <div className="w-16 h-16 bg-slate-700/50 rounded-full flex items-center justify-center mx-auto mb-4 text-text-muted">
                        <FolderOpen size={32} />
                    </div>
                    <h4 className="text-lg font-medium text-white mb-2">尚無任何專案</h4>
                    <p className="text-text-muted mb-6">點擊下方按鈕建立你的第一個採購專案。</p>
                    <button
                        onClick={handleCreateProject}
                        disabled={creating}
                        className="text-primary hover:text-primary-hover font-medium underline"
                    >
                        立即建立專案
                    </button>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {projects.map((project) => (
                        <Link to={`/project/${project.id}`} key={project.id} className="bg-surface border border-slate-700 rounded-xl p-6 hover:border-primary/50 transition-all cursor-pointer group block">
                            <div className="flex justify-between items-start mb-4">
                                <div className="p-3 bg-blue-500/10 rounded-lg text-blue-400 group-hover:bg-blue-500/20 transition-colors">
                                    <FolderOpen size={24} />
                                </div>
                                <div className="flex flex-col items-end gap-1">
                                    <span className="text-xs font-mono text-slate-500 bg-slate-900/50 px-2 py-1 rounded">
                                        {project.id.split('_')[0]}
                                    </span>
                                    <span className="text-xs font-medium text-accent bg-accent/10 px-2 py-1 rounded">
                                        共 {project.item_count} 款卡片
                                    </span>
                                </div>
                            </div>
                            <h4 className="text-lg font-medium text-white mb-2 truncate">{project.id}</h4>

                            {/* 專案卡片預覽 */}
                            {project.item_count > 0 ? (
                                <div className="flex flex-wrap gap-1 mb-2">
                                    {project.preview_names.map((name, idx) => (
                                        <span key={idx} className="text-[11px] text-slate-400 bg-slate-800 px-2 py-0.5 rounded truncate max-w-[120px]">
                                            {name}
                                        </span>
                                    ))}
                                    {project.item_count > 3 && (
                                        <span className="text-[11px] text-slate-500 bg-slate-800/50 px-2 py-0.5 rounded">
                                            +{project.item_count - 3}
                                        </span>
                                    )}
                                </div>
                            ) : (
                                <p className="text-sm text-text-muted mb-2">空購物車</p>
                            )}

                            <p className="text-xs text-text-muted/70 flex items-center gap-1 mt-4">
                                點擊開啟此專案
                            </p>
                        </Link>
                    ))}
                </div>
            )}
        </div>
    );
};

export default ProjectList;
