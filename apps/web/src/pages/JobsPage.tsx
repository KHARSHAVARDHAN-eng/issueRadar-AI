import React, { useEffect, useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { fetchSyncJobs, retrySyncJob } from '../services/api';
import { SyncJob } from '../types/automation';
import {
  AlertCircle,
  CheckCircle2,
  Clock,
  Cpu,
  FolderGit2,
  LayoutDashboard,
  ListTodo,
  Loader2,
  LogOut,
  RefreshCw,
  Zap,
} from 'lucide-react';

interface JobsPageProps {
  onNavigateToDashboard: () => void;
  onNavigateToRepositories: () => void;
  onNavigateToIssues: () => void;
}

export const JobsPage: React.FC<JobsPageProps> = ({
  onNavigateToDashboard,
  onNavigateToRepositories,
  onNavigateToIssues,
}) => {
  const { user, logout } = useAuth();
  const [jobs, setJobs] = useState<SyncJob[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [retryingId, setRetryingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadJobs = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchSyncJobs();
      setJobs(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load sync jobs');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadJobs();
  }, []);

  const handleRetry = async (jobId: string) => {
    setRetryingId(jobId);
    try {
      await retrySyncJob(jobId);
      await loadJobs();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to retry sync job');
    } finally {
      setRetryingId(null);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return (
          <span
            style={{
              padding: '0.125rem 0.5rem',
              borderRadius: '9999px',
              background: 'rgba(16, 185, 129, 0.15)',
              color: '#34d399',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              fontWeight: 600,
              fontSize: '0.75rem',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.25rem',
            }}
          >
            <CheckCircle2 className="w-3 h-3" /> Completed
          </span>
        );
      case 'running':
        return (
          <span
            style={{
              padding: '0.125rem 0.5rem',
              borderRadius: '9999px',
              background: 'rgba(59, 130, 246, 0.15)',
              color: '#60a5fa',
              border: '1px solid rgba(59, 130, 246, 0.3)',
              fontWeight: 600,
              fontSize: '0.75rem',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.25rem',
            }}
          >
            <Loader2 className="w-3 h-3 animate-spin" /> Running
          </span>
        );
      case 'failed':
        return (
          <span
            style={{
              padding: '0.125rem 0.5rem',
              borderRadius: '9999px',
              background: 'rgba(239, 68, 68, 0.15)',
              color: '#f87171',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              fontWeight: 600,
              fontSize: '0.75rem',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.25rem',
            }}
          >
            <AlertCircle className="w-3 h-3" /> Failed
          </span>
        );
      default:
        return (
          <span
            style={{
              padding: '0.125rem 0.5rem',
              borderRadius: '9999px',
              background: 'rgba(245, 158, 11, 0.15)',
              color: '#fbbf24',
              border: '1px solid rgba(245, 158, 11, 0.3)',
              fontWeight: 600,
              fontSize: '0.75rem',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.25rem',
            }}
          >
            <Clock className="w-3 h-3" /> Queued
          </span>
        );
    }
  };

  return (
    <div className="app-container">
      {/* Header */}
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
              onClick={onNavigateToRepositories}
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
              <Cpu className="w-4 h-4 text-blue-400" />
              <span>Sync Job Monitor</span>
            </button>
          </nav>
        </div>

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

      {/* Main Content */}
      <section
        style={{
          marginBottom: '1.5rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div>
          <h2 className="hero-title" style={{ textAlign: 'left', fontSize: '2.25rem' }}>
            Sync Job <span>Monitor</span>
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '1rem' }}>
            Background sync jobs, worker execution statuses, and manual retry controls.
          </p>
        </div>

        <button
          onClick={loadJobs}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.375rem',
            padding: '0.5rem 0.875rem',
            background: 'rgba(255,255,255,0.05)',
            border: '1px solid var(--border-color)',
            color: 'var(--text-primary)',
            borderRadius: '0.5rem',
            fontSize: '0.8125rem',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> Refresh
        </button>
      </section>

      {loading ? (
        <div style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <Loader2 className="w-8 h-8 animate-spin" style={{ margin: '0 auto 1rem auto' }} />
          <p>Loading sync jobs...</p>
        </div>
      ) : error ? (
        <div className="card" style={{ padding: '2rem', textAlign: 'center', color: '#f87171' }}>
          <AlertCircle className="w-8 h-8" style={{ margin: '0 auto 1rem auto' }} />
          <p>{error}</p>
        </div>
      ) : jobs.length === 0 ? (
        <div className="card" style={{ padding: '4rem 2rem', textAlign: 'center' }}>
          <Cpu className="w-10 h-10 text-muted" style={{ margin: '0 auto 1.25rem auto' }} />
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.5rem' }}>
            No Background Jobs
          </h3>
          <p style={{ color: 'var(--text-secondary)' }}>
            Sync jobs triggered by repository sync actions will be logged here.
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
          {jobs.map((job) => (
            <div
              key={job.id}
              className="card"
              style={{
                padding: '1.25rem 1.5rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '1rem',
              }}
            >
              <div>
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.75rem',
                    marginBottom: '0.375rem',
                  }}
                >
                  {getStatusBadge(job.status)}
                  <h4
                    style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}
                  >
                    {job.repository ? job.repository.full_name : `Repo ${job.repository_id}`}
                  </h4>
                </div>

                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '1.25rem',
                    fontSize: '0.8125rem',
                    color: 'var(--text-secondary)',
                  }}
                >
                  <span>
                    Processed: <strong>{job.issues_processed} issues</strong>
                  </span>
                  <span>
                    Started:{' '}
                    {job.started_at ? new Date(job.started_at).toLocaleTimeString() : 'Queued'}
                  </span>
                  <span>
                    Finished:{' '}
                    {job.finished_at
                      ? new Date(job.finished_at).toLocaleTimeString()
                      : 'In Progress'}
                  </span>
                </div>

                {job.errors && (
                  <p
                    style={{
                      fontSize: '0.8125rem',
                      color: '#f87171',
                      marginTop: '0.375rem',
                      fontFamily: 'var(--font-mono)',
                    }}
                  >
                    Error: {job.errors}
                  </p>
                )}
              </div>

              <button
                onClick={() => handleRetry(job.id)}
                disabled={retryingId === job.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.375rem',
                  padding: '0.5rem 0.875rem',
                  background: 'rgba(59, 130, 246, 0.15)',
                  border: '1px solid rgba(59, 130, 246, 0.3)',
                  color: '#93c5fd',
                  borderRadius: '0.5rem',
                  fontSize: '0.8125rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                <RefreshCw
                  className={`w-3.5 h-3.5 ${retryingId === job.id ? 'animate-spin' : ''}`}
                />
                <span>{retryingId === job.id ? 'Retrying...' : 'Retry Job'}</span>
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
