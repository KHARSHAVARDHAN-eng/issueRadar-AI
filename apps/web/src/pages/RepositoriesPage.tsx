import React, { useEffect, useState } from 'react';
import { AddRepositoryModal } from '../components/AddRepositoryModal';
import { useAuth } from '../hooks/useAuth';
import {
  analyzeRepository,
  deleteRepository,
  fetchRepositories,
  fetchSyncJobs,
  syncRepository,
} from '../services/api';
import { SyncJob } from '../types/automation';
import { Repository } from '../types/repository';
import {
  AlertCircle,
  BrainCircuit,
  Cpu,
  FolderGit2,
  GitFork,
  Globe,
  LayoutDashboard,
  ListTodo,
  Loader2,
  LogOut,
  Plus,
  RefreshCw,
  Star,
  Trash2,
  Zap,
} from 'lucide-react';

interface RepositoriesPageProps {
  onNavigateToDashboard: () => void;
  onNavigateToIssues: () => void;
}

export const RepositoriesPage: React.FC<RepositoriesPageProps> = ({
  onNavigateToDashboard,
  onNavigateToIssues,
}) => {
  const { user, logout } = useAuth();

  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [jobs, setJobs] = useState<SyncJob[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [isAddModalOpen, setIsAddModalOpen] = useState<boolean>(false);
  const [syncingRepoId, setSyncingRepoId] = useState<string | null>(null);
  const [analyzingRepoId, setAnalyzingRepoId] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [reposData, jobsData] = await Promise.all([fetchRepositories(), fetchSyncJobs()]);
      setRepositories(reposData);
      setJobs(jobsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load repositories');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    // Live polling for background sync jobs
    const interval = setInterval(async () => {
      try {
        const [reposData, jobsData] = await Promise.all([fetchRepositories(), fetchSyncJobs()]);
        setRepositories(reposData);
        setJobs(jobsData);
      } catch (err) {
        // Silent poll error
      }
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleSyncRepository = async (repoId: string) => {
    setSyncingRepoId(repoId);
    try {
      await syncRepository(repoId);
      // Immediately refresh jobs to show Queued status
      const updatedJobs = await fetchSyncJobs();
      setJobs(updatedJobs);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to enqueue repository sync');
    } finally {
      setSyncingRepoId(null);
    }
  };

  const handleAnalyzeRepository = async (repoId: string) => {
    setAnalyzingRepoId(repoId);
    try {
      const res = await analyzeRepository(repoId);
      alert(`Successfully analyzed ${res.analyzed_count} issues with AI!`);
      await loadData();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to analyze repository');
    } finally {
      setAnalyzingRepoId(null);
    }
  };

  const handleDeleteRepository = async (repoId: string, fullName: string) => {
    if (!confirm(`Are you sure you want to delete repository "${fullName}"?`)) return;
    try {
      await deleteRepository(repoId);
      setRepositories((prev) => prev.filter((r) => r.id !== repoId));
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete repository');
    }
  };

  const getLatestJobForRepo = (repoId: string) => {
    return jobs.find((j) => j.repository_id === repoId);
  };

  return (
    <div className="app-container">
      {/* Navigation Header */}
      <header className="app-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
          <div className="brand">
            <div className="brand-icon">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <h1 className="brand-title">IssueRadar AI</h1>
          </div>

          <nav style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              onClick={onNavigateToDashboard}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.5rem 0.875rem',
                background: 'transparent',
                border: 'none',
                color: 'var(--text-secondary)',
                borderRadius: '0.5rem',
                fontSize: '0.875rem',
                fontWeight: 500,
                cursor: 'pointer',
              }}
            >
              <LayoutDashboard className="w-4 h-4" />
              <span>Dashboard</span>
            </button>

            <button
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.5rem 0.875rem',
                background: 'rgba(59, 130, 246, 0.15)',
                border: '1px solid rgba(59, 130, 246, 0.3)',
                color: '#93c5fd',
                borderRadius: '0.5rem',
                fontSize: '0.875rem',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              <FolderGit2 className="w-4 h-4" />
              <span>Repositories</span>
            </button>

            <button
              onClick={onNavigateToIssues}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.5rem 0.875rem',
                background: 'transparent',
                border: 'none',
                color: 'var(--text-secondary)',
                borderRadius: '0.5rem',
                fontSize: '0.875rem',
                fontWeight: 500,
                cursor: 'pointer',
              }}
            >
              <ListTodo className="w-4 h-4" />
              <span>Smart Search</span>
            </button>
          </nav>
        </div>

        {/* User Profile & Logout */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {user?.avatar_url && (
            <img
              src={user.avatar_url}
              alt={user.username}
              style={{ width: '2.25rem', height: '2.25rem', borderRadius: '50%' }}
            />
          )}
          <button
            onClick={logout}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.375rem',
              padding: '0.4rem 0.75rem',
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.25)',
              color: '#f87171',
              borderRadius: '0.5rem',
              fontSize: '0.8125rem',
              fontWeight: 500,
              cursor: 'pointer',
            }}
          >
            <LogOut className="w-4 h-4" />
            <span>Logout</span>
          </button>
        </div>
      </header>

      {/* Hero Action Header */}
      <section
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '2.5rem',
          flexWrap: 'wrap',
          gap: '1rem',
        }}
      >
        <div>
          <h2 className="hero-title" style={{ textAlign: 'left', fontSize: '2.25rem' }}>
            Monitored <span>Repositories</span>
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '1rem' }}>
            Track open-source GitHub repositories for background issue sync and AI scoring.
          </p>
        </div>

        <button
          onClick={() => setIsAddModalOpen(true)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.625rem 1.25rem',
            background: 'var(--accent-blue)',
            color: '#ffffff',
            border: 'none',
            borderRadius: '0.5rem',
            fontWeight: 600,
            fontSize: '0.9375rem',
            cursor: 'pointer',
            boxShadow: '0 4px 14px rgba(59, 130, 246, 0.35)',
          }}
        >
          <Plus className="w-4 h-4" />
          <span>Add Repository</span>
        </button>
      </section>

      {/* Main Grid View */}
      {loading ? (
        <div style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <Loader2 className="w-8 h-8 animate-spin" style={{ margin: '0 auto 1rem auto' }} />
          <p>Loading tracked repositories...</p>
        </div>
      ) : error ? (
        <div className="card" style={{ padding: '2rem', textAlign: 'center', color: '#f87171' }}>
          <AlertCircle className="w-8 h-8" style={{ margin: '0 auto 1rem auto' }} />
          <p>{error}</p>
        </div>
      ) : repositories.length === 0 ? (
        <div className="card" style={{ padding: '4rem 2rem', textAlign: 'center' }}>
          <FolderGit2 className="w-12 h-12 text-muted" style={{ margin: '0 auto 1.5rem auto' }} />
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.5rem' }}>
            No Repositories Tracked Yet
          </h3>
          <p
            style={{
              color: 'var(--text-secondary)',
              marginBottom: '1.5rem',
              maxWidth: '480px',
              margin: '0 auto 1.5rem auto',
            }}
          >
            Add your first open-source GitHub repository to begin automatic issue discovery and
            scoring.
          </p>
          <button
            onClick={() => setIsAddModalOpen(true)}
            style={{
              padding: '0.625rem 1.25rem',
              background: 'var(--accent-blue)',
              color: '#ffffff',
              border: 'none',
              borderRadius: '0.5rem',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            Add Repository Now
          </button>
        </div>
      ) : (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
            gap: '1.5rem',
          }}
        >
          {repositories.map((repo) => {
            const latestJob = getLatestJobForRepo(repo.id);

            return (
              <div
                key={repo.id}
                className="card"
                style={{
                  padding: '1.5rem',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  border: '1px solid var(--border-color)',
                  position: 'relative',
                }}
              >
                <div>
                  {/* Repo Owner/Name Header */}
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'flex-start',
                      marginBottom: '0.75rem',
                    }}
                  >
                    <div>
                      <span
                        style={{
                          fontSize: '0.8125rem',
                          color: 'var(--text-secondary)',
                          display: 'block',
                        }}
                      >
                        {repo.owner}
                      </span>
                      <h3
                        style={{
                          fontSize: '1.25rem',
                          fontWeight: 700,
                          color: 'var(--text-primary)',
                          margin: 0,
                        }}
                      >
                        {repo.name}
                      </h3>
                    </div>

                    <button
                      onClick={() => handleDeleteRepository(repo.id, repo.full_name)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: 'var(--text-muted)',
                        cursor: 'pointer',
                        padding: '0.25rem',
                        borderRadius: '0.375rem',
                      }}
                      title="Remove Repository"
                    >
                      <Trash2 className="w-4 h-4 text-red-400" />
                    </button>
                  </div>

                  {/* Repository Description */}
                  <p
                    style={{
                      fontSize: '0.875rem',
                      color: 'var(--text-secondary)',
                      marginBottom: '1.25rem',
                      height: '2.5rem',
                      overflow: 'hidden',
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                    }}
                  >
                    {repo.description || 'No description provided for this repository.'}
                  </p>

                  {/* Metadata Pills */}
                  <div
                    style={{
                      display: 'flex',
                      flexWrap: 'wrap',
                      gap: '0.75rem',
                      marginBottom: '1.25rem',
                      fontSize: '0.8125rem',
                      color: 'var(--text-muted)',
                    }}
                  >
                    {repo.language && (
                      <span
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.25rem',
                          color: '#93c5fd',
                        }}
                      >
                        <Globe className="w-3.5 h-3.5" /> {repo.language}
                      </span>
                    )}
                    <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                      <Star className="w-3.5 h-3.5 text-amber-400" /> {repo.stars.toLocaleString()}
                    </span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                      <GitFork className="w-3.5 h-3.5" /> {repo.forks.toLocaleString()}
                    </span>
                  </div>

                  {/* Worker Sync Progress Bar & Live Job Indicator */}
                  {latestJob && (
                    <div
                      style={{
                        marginBottom: '1.25rem',
                        background: 'rgba(255, 255, 255, 0.03)',
                        padding: '0.75rem',
                        borderRadius: '0.5rem',
                        border: '1px solid var(--border-color)',
                      }}
                    >
                      <div
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          marginBottom: '0.375rem',
                        }}
                      >
                        <span
                          style={{
                            fontSize: '0.75rem',
                            color: 'var(--text-secondary)',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.375rem',
                          }}
                        >
                          <Cpu className="w-3.5 h-3.5 text-blue-400" /> Worker Job:{' '}
                          <strong>{latestJob.status}</strong>
                        </span>
                        <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#93c5fd' }}>
                          {latestJob.status === 'completed'
                            ? '100%'
                            : latestJob.status === 'running'
                              ? '50%'
                              : '0%'}
                        </span>
                      </div>
                      <div
                        style={{
                          width: '100%',
                          height: '4px',
                          background: 'rgba(255,255,255,0.1)',
                          borderRadius: '2px',
                          overflow: 'hidden',
                        }}
                      >
                        <div
                          style={{
                            height: '100%',
                            width:
                              latestJob.status === 'completed'
                                ? '100%'
                                : latestJob.status === 'running'
                                  ? '50%'
                                  : '10%',
                            background:
                              latestJob.status === 'failed' ? '#f87171' : 'var(--accent-blue)',
                            transition: 'width 0.5s ease',
                          }}
                        />
                      </div>
                    </div>
                  )}
                </div>

                {/* Card Action Controls */}
                <div
                  style={{
                    paddingTop: '1rem',
                    borderTop: '1px solid var(--border-color)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.5rem',
                  }}
                >
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button
                      onClick={() => handleSyncRepository(repo.id)}
                      disabled={syncingRepoId === repo.id}
                      style={{
                        flex: 1,
                        padding: '0.5rem',
                        background: 'rgba(59, 130, 246, 0.15)',
                        border: '1px solid rgba(59, 130, 246, 0.3)',
                        color: '#93c5fd',
                        borderRadius: '0.375rem',
                        fontSize: '0.8125rem',
                        fontWeight: 600,
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '0.375rem',
                      }}
                    >
                      <RefreshCw
                        className={`w-3.5 h-3.5 ${syncingRepoId === repo.id ? 'animate-spin' : ''}`}
                      />
                      <span>{syncingRepoId === repo.id ? 'Starting...' : 'Start Sync'}</span>
                    </button>

                    <button
                      onClick={() => handleAnalyzeRepository(repo.id)}
                      disabled={analyzingRepoId === repo.id}
                      style={{
                        flex: 1,
                        padding: '0.5rem',
                        background: 'rgba(139, 92, 246, 0.15)',
                        border: '1px solid rgba(139, 92, 246, 0.3)',
                        color: '#c084fc',
                        borderRadius: '0.375rem',
                        fontSize: '0.8125rem',
                        fontWeight: 600,
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '0.375rem',
                      }}
                    >
                      <BrainCircuit
                        className={`w-3.5 h-3.5 ${analyzingRepoId === repo.id ? 'animate-spin' : ''}`}
                      />
                      <span>{analyzingRepoId === repo.id ? 'Analyzing...' : 'AI Analysis'}</span>
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Add Repository Modal */}
      <AddRepositoryModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onSuccess={loadData}
      />
    </div>
  );
};
