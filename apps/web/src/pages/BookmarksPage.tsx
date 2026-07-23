import React, { useEffect, useState } from 'react';
import { IssueDetailModal } from '../components/IssueDetailModal';
import { useAuth } from '../hooks/useAuth';
import { deleteBookmark, fetchBookmarks } from '../services/api';
import { Bookmark as BookmarkType } from '../types/automation';
import {
  AlertCircle,
  Bookmark as BookmarkIcon,
  FolderGit2,
  GitPullRequest,
  LayoutDashboard,
  ListTodo,
  Loader2,
  LogOut,
  Trash2,
  Zap,
} from 'lucide-react';

interface BookmarksPageProps {
  onNavigateToDashboard: () => void;
  onNavigateToRepositories: () => void;
  onNavigateToIssues: () => void;
}

export const BookmarksPage: React.FC<BookmarksPageProps> = ({
  onNavigateToDashboard,
  onNavigateToRepositories,
  onNavigateToIssues,
}) => {
  const { user, logout } = useAuth();
  const [bookmarks, setBookmarks] = useState<BookmarkType[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedIssueId, setSelectedIssueId] = useState<string | null>(null);

  const loadBookmarks = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchBookmarks();
      setBookmarks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load bookmarks');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBookmarks();
  }, []);

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await deleteBookmark(id);
      setBookmarks((prev) => prev.filter((b) => b.id !== id && b.issue_id !== id));
    } catch (err) {
      alert('Failed to remove bookmark');
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
              <BookmarkIcon className="w-4 h-4 text-blue-400" />
              <span>Bookmarks</span>
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
      <section style={{ marginBottom: '2rem' }}>
        <h2 className="hero-title" style={{ textAlign: 'left', fontSize: '2.25rem' }}>
          Bookmarked <span>Issues</span>
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1rem' }}>
          Saved issues pinned for active development and technical reference.
        </p>
      </section>

      {loading ? (
        <div style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <Loader2 className="w-8 h-8 animate-spin" style={{ margin: '0 auto 1rem auto' }} />
          <p>Loading bookmarks...</p>
        </div>
      ) : error ? (
        <div className="card" style={{ padding: '2rem', textAlign: 'center', color: '#f87171' }}>
          <AlertCircle className="w-8 h-8" style={{ margin: '0 auto 1rem auto' }} />
          <p>{error}</p>
        </div>
      ) : bookmarks.length === 0 ? (
        <div className="card" style={{ padding: '4rem 2rem', textAlign: 'center' }}>
          <BookmarkIcon
            className="w-10 h-10 text-muted"
            style={{ margin: '0 auto 1.25rem auto' }}
          />
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.5rem' }}>
            No Pinned Bookmarks
          </h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
            Bookmark high-impact open-source issues to track your progress and take notes.
          </p>
          <button
            onClick={onNavigateToIssues}
            style={{
              padding: '0.625rem 1.25rem',
              background: 'var(--accent-blue)',
              color: '#fff',
              border: 'none',
              borderRadius: '0.5rem',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            Explore Smart Search
          </button>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {bookmarks.map((bm) => (
            <div
              key={bm.id}
              className="card"
              style={{
                padding: '1.25rem 1.5rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'flex-start',
                justifyContent: 'space-between',
                gap: '1rem',
              }}
              onClick={() => setSelectedIssueId(bm.issue_id)}
            >
              <div style={{ flexGrow: 1 }}>
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.625rem',
                    marginBottom: '0.5rem',
                  }}
                >
                  {bm.issue?.is_pull_request ? (
                    <GitPullRequest className="w-5 h-5 text-purple-400" />
                  ) : (
                    <AlertCircle className="w-5 h-5 text-emerald-400" />
                  )}
                  <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                    {bm.issue ? bm.issue.title : `Issue ${bm.issue_id}`}
                  </h4>
                </div>

                {bm.notes && (
                  <p
                    style={{
                      fontSize: '0.875rem',
                      color: 'var(--accent-blue)',
                      background: 'rgba(59, 130, 246, 0.08)',
                      padding: '0.5rem 0.75rem',
                      borderRadius: '0.375rem',
                      border: '1px solid rgba(59, 130, 246, 0.2)',
                      marginBottom: '0.5rem',
                    }}
                  >
                    📝 Notes: {bm.notes}
                  </p>
                )}

                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Bookmarked on {new Date(bm.created_at).toLocaleDateString()}
                </span>
              </div>

              <button
                onClick={(e) => handleDelete(bm.id, e)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#f87171',
                  cursor: 'pointer',
                  padding: '0.375rem',
                }}
              >
                <Trash2 className="w-5 h-5" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      <IssueDetailModal issueId={selectedIssueId} onClose={() => setSelectedIssueId(null)} />
    </div>
  );
};
