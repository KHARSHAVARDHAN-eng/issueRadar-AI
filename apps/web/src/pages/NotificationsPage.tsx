import React, { useEffect, useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import {
  deleteNotification,
  fetchNotifications,
  markAllNotificationsRead,
  markNotificationRead,
} from '../services/api';
import { NotificationItem } from '../types/automation';
import {
  AlertCircle,
  Bell,
  CheckCheck,
  FolderGit2,
  LayoutDashboard,
  ListTodo,
  Loader2,
  LogOut,
  Trash2,
  Zap,
} from 'lucide-react';

interface NotificationsPageProps {
  onNavigateToDashboard: () => void;
  onNavigateToRepositories: () => void;
  onNavigateToIssues: () => void;
}

export const NotificationsPage: React.FC<NotificationsPageProps> = ({
  onNavigateToDashboard,
  onNavigateToRepositories,
  onNavigateToIssues,
}) => {
  const { user, logout } = useAuth();
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadOnly, setUnreadOnly] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadNotifs = React.useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchNotifications(unreadOnly);
      setNotifications(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load notifications');
    } finally {
      setLoading(false);
    }
  }, [unreadOnly]);

  useEffect(() => {
    loadNotifs();
  }, [loadNotifs]);

  const handleMarkRead = async (id: string) => {
    try {
      await markNotificationRead(id);
      setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)));
    } catch (err) {
      alert('Failed to mark notification as read');
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await markAllNotificationsRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
    } catch (err) {
      alert('Failed to mark all as read');
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteNotification(id);
      setNotifications((prev) => prev.filter((n) => n.id !== id));
    } catch (err) {
      alert('Failed to delete notification');
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
              <Bell className="w-4 h-4 text-blue-400" />
              <span>Notifications</span>
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
          flexWrap: 'wrap',
        }}
      >
        <div>
          <h2 className="hero-title" style={{ textAlign: 'left', fontSize: '2.25rem' }}>
            Automated <span>Notifications</span>
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '1rem' }}>
            Live alerts generated when newly synced issues match your saved searches.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <button
            onClick={() => setUnreadOnly(!unreadOnly)}
            style={{
              padding: '0.5rem 0.875rem',
              borderRadius: '0.5rem',
              border: '1px solid var(--border-color)',
              background: unreadOnly ? 'var(--accent-blue)' : 'rgba(255,255,255,0.05)',
              color: '#fff',
              fontSize: '0.8125rem',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            {unreadOnly ? 'Showing Unread' : 'Filter Unread'}
          </button>

          <button
            onClick={handleMarkAllRead}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.375rem',
              padding: '0.5rem 0.875rem',
              borderRadius: '0.5rem',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              background: 'rgba(16, 185, 129, 0.15)',
              color: '#34d399',
              fontSize: '0.8125rem',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            <CheckCheck className="w-4 h-4" /> Mark All Read
          </button>
        </div>
      </section>

      {loading ? (
        <div style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <Loader2 className="w-8 h-8 animate-spin" style={{ margin: '0 auto 1rem auto' }} />
          <p>Loading notifications...</p>
        </div>
      ) : error ? (
        <div className="card" style={{ padding: '2rem', textAlign: 'center', color: '#f87171' }}>
          <AlertCircle className="w-8 h-8" style={{ margin: '0 auto 1rem auto' }} />
          <p>{error}</p>
        </div>
      ) : notifications.length === 0 ? (
        <div className="card" style={{ padding: '4rem 2rem', textAlign: 'center' }}>
          <Bell className="w-10 h-10 text-muted" style={{ margin: '0 auto 1.25rem auto' }} />
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.5rem' }}>
            No Notifications Found
          </h3>
          <p style={{ color: 'var(--text-secondary)' }}>
            You are all caught up! New matching issue alerts will appear here automatically.
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
          {notifications.map((n) => (
            <div
              key={n.id}
              className="card"
              style={{
                padding: '1.25rem 1.5rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '1rem',
                borderLeft: n.is_read
                  ? '1px solid var(--border-color)'
                  : '4px solid var(--accent-blue)',
                opacity: n.is_read ? 0.75 : 1,
              }}
            >
              <div>
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    marginBottom: '0.375rem',
                  }}
                >
                  <span
                    style={{
                      fontSize: '0.75rem',
                      padding: '0.125rem 0.5rem',
                      borderRadius: '9999px',
                      background: 'rgba(59, 130, 246, 0.15)',
                      color: '#93c5fd',
                      border: '1px solid rgba(59, 130, 246, 0.3)',
                      fontWeight: 600,
                    }}
                  >
                    {n.type.replace(/_/g, ' ')}
                  </span>
                  <h4
                    style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}
                  >
                    {n.title}
                  </h4>
                </div>
                <p
                  style={{
                    fontSize: '0.875rem',
                    color: 'var(--text-secondary)',
                    marginBottom: '0.375rem',
                  }}
                >
                  {n.message}
                </p>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Received {new Date(n.created_at).toLocaleString()}
                </span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                {!n.is_read && (
                  <button
                    onClick={() => handleMarkRead(n.id)}
                    style={{
                      padding: '0.375rem 0.625rem',
                      borderRadius: '0.375rem',
                      border: '1px solid rgba(16, 185, 129, 0.3)',
                      background: 'rgba(16, 185, 129, 0.15)',
                      color: '#34d399',
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      cursor: 'pointer',
                    }}
                  >
                    Mark Read
                  </button>
                )}
                <button
                  onClick={() => handleDelete(n.id)}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: '#f87171',
                    cursor: 'pointer',
                    padding: '0.375rem',
                  }}
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
