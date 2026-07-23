import React, { useEffect, useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { fetchNotifications, fetchRepositories, fetchSyncJobs } from '../services/api';
import { NotificationItem, SyncJob } from '../types/automation';
import { Repository } from '../types/repository';
import {
  Bell,
  Clock,
  Cpu,
  FolderGit2,
  ListTodo,
  LogOut,
  RefreshCw,
  Sparkles,
  Zap,
} from 'lucide-react';

interface DashboardPageProps {
  onNavigateToRepositories: () => void;
  onNavigateToIssues: () => void;
  onNavigateToSavedSearches: () => void;
  onNavigateToBookmarks: () => void;
  onNavigateToNotifications: () => void;
  onNavigateToJobs: () => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  onNavigateToRepositories,
  onNavigateToIssues,
  onNavigateToSavedSearches,
  onNavigateToBookmarks,
  onNavigateToNotifications,
  onNavigateToJobs,
}) => {
  const { user, logout } = useAuth();

  const [repos, setRepos] = useState<Repository[]>([]);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [jobs, setJobs] = useState<SyncJob[]>([]);

  useEffect(() => {
    fetchRepositories().then(setRepos).catch(console.error);
    fetchNotifications(true).then(setNotifications).catch(console.error);
    fetchSyncJobs().then(setJobs).catch(console.error);
  }, []);

  const syncingReposCount = repos.filter(
    (r) => r.sync_status === 'in_progress' || r.sync_status === 'syncing',
  ).length;
  const pendingJobsCount = jobs.filter(
    (j) => j.status === 'running' || j.status === 'queued',
  ).length;
  const lastSyncJob = jobs[0];

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
              <Sparkles className="w-4 h-4" />
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

      {/* Hero Welcome */}
      <section style={{ marginBottom: '2.5rem' }}>
        <h2 className="hero-title" style={{ textAlign: 'left', fontSize: '2.5rem' }}>
          Welcome back, <span>{user?.username || 'Contributor'}</span>!
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.05rem', maxWidth: '640px' }}>
          Production AI Provider Engine & Celery background worker statistics, active syncs, and
          issue alerts.
        </p>
      </section>

      {/* Production AI & Worker Stats Cards */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '1.25rem',
          marginBottom: '2.5rem',
        }}
      >
        <div
          className="card"
          style={{ padding: '1.25rem', cursor: 'pointer' }}
          onClick={onNavigateToRepositories}
        >
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '0.75rem',
            }}
          >
            <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
              Repositories Syncing
            </span>
            <RefreshCw className="w-5 h-5 text-blue-400" />
          </div>
          <span style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--text-primary)' }}>
            {syncingReposCount}
          </span>
          <span
            style={{
              fontSize: '0.75rem',
              color: 'var(--text-muted)',
              display: 'block',
              marginTop: '0.25rem',
            }}
          >
            {repos.length} total repositories
          </span>
        </div>

        <div
          className="card"
          style={{ padding: '1.25rem', cursor: 'pointer' }}
          onClick={onNavigateToJobs}
        >
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '0.75rem',
            }}
          >
            <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
              Active Celery Jobs
            </span>
            <Cpu className="w-5 h-5 text-purple-400" />
          </div>
          <span style={{ fontSize: '2rem', fontWeight: 800, color: '#c084fc' }}>
            {pendingJobsCount}
          </span>
          <span
            style={{
              fontSize: '0.75rem',
              color: 'var(--text-muted)',
              display: 'block',
              marginTop: '0.25rem',
            }}
          >
            Worker execution queue
          </span>
        </div>

        <div
          className="card"
          style={{ padding: '1.25rem', cursor: 'pointer' }}
          onClick={onNavigateToNotifications}
        >
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '0.75rem',
            }}
          >
            <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
              Notifications Generated
            </span>
            <Bell className="w-5 h-5 text-emerald-400" />
          </div>
          <span style={{ fontSize: '2rem', fontWeight: 800, color: '#34d399' }}>
            {notifications.length}
          </span>
          <span
            style={{
              fontSize: '0.75rem',
              color: 'var(--text-muted)',
              display: 'block',
              marginTop: '0.25rem',
            }}
          >
            Matching issue alerts
          </span>
        </div>

        <div
          className="card"
          style={{ padding: '1.25rem', cursor: 'pointer' }}
          onClick={onNavigateToJobs}
        >
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '0.75rem',
            }}
          >
            <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Last Sync</span>
            <Clock className="w-5 h-5 text-amber-400" />
          </div>
          <span style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fbbf24' }}>
            {lastSyncJob?.finished_at
              ? new Date(lastSyncJob.finished_at).toLocaleTimeString()
              : 'Recent'}
          </span>
          <span
            style={{
              fontSize: '0.75rem',
              color: 'var(--text-muted)',
              display: 'block',
              marginTop: '0.25rem',
            }}
          >
            {lastSyncJob ? `${lastSyncJob.issues_processed} issues synced` : 'No recent syncs'}
          </span>
        </div>
      </div>

      {/* Navigation Panel */}
      <section className="card" style={{ padding: '2rem' }}>
        <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1rem' }}>
          Platform Control Panel
        </h3>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '1rem',
          }}
        >
          <button
            onClick={onNavigateToRepositories}
            style={{
              padding: '1rem',
              background: 'rgba(59, 130, 246, 0.12)',
              border: '1px solid rgba(59, 130, 246, 0.3)',
              borderRadius: '0.5rem',
              color: '#93c5fd',
              fontWeight: 600,
              fontSize: '0.9375rem',
              cursor: 'pointer',
              textAlign: 'left',
            }}
          >
            ⚙️ Repository Sync & AI →
          </button>

          <button
            onClick={onNavigateToSavedSearches}
            style={{
              padding: '1rem',
              background: 'rgba(139, 92, 246, 0.12)',
              border: '1px solid rgba(139, 92, 246, 0.3)',
              borderRadius: '0.5rem',
              color: '#c084fc',
              fontWeight: 600,
              fontSize: '0.9375rem',
              cursor: 'pointer',
              textAlign: 'left',
            }}
          >
            🔖 Saved Searches →
          </button>

          <button
            onClick={onNavigateToBookmarks}
            style={{
              padding: '1rem',
              background: 'rgba(16, 185, 129, 0.12)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              borderRadius: '0.5rem',
              color: '#34d399',
              fontWeight: 600,
              fontSize: '0.9375rem',
              cursor: 'pointer',
              textAlign: 'left',
            }}
          >
            📌 Pinned Bookmarks →
          </button>

          <button
            onClick={onNavigateToJobs}
            style={{
              padding: '1rem',
              background: 'rgba(245, 158, 11, 0.12)',
              border: '1px solid rgba(245, 158, 11, 0.3)',
              borderRadius: '0.5rem',
              color: '#fbbf24',
              fontWeight: 600,
              fontSize: '0.9375rem',
              cursor: 'pointer',
              textAlign: 'left',
            }}
          >
            ⚡ Celery Background Jobs →
          </button>
        </div>
      </section>
    </div>
  );
};
