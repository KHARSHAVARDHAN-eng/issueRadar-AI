import React, { useEffect, useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { deleteSavedSearch, fetchSavedSearches } from '../services/api';
import { SavedSearch } from '../types/automation';
import {
  AlertCircle,
  Bookmark,
  FolderGit2,
  LayoutDashboard,
  ListTodo,
  Loader2,
  LogOut,
  Search,
  Trash2,
  Zap,
} from 'lucide-react';

interface SavedSearchesPageProps {
  onNavigateToDashboard: () => void;
  onNavigateToRepositories: () => void;
  onNavigateToIssues: (params?: Record<string, string>) => void;
}

export const SavedSearchesPage: React.FC<SavedSearchesPageProps> = ({
  onNavigateToDashboard,
  onNavigateToRepositories,
  onNavigateToIssues,
}) => {
  const { user, logout } = useAuth();
  const [searches, setSearches] = useState<SavedSearch[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadSavedSearches = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchSavedSearches();
      setSearches(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load saved searches');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSavedSearches();
  }, []);

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this saved search?')) return;
    try {
      await deleteSavedSearch(id);
      setSearches((prev) => prev.filter((s) => s.id !== id));
    } catch (err) {
      alert('Failed to delete saved search');
    }
  };

  const handleRunSearch = (searchObj: SavedSearch) => {
    const params: Record<string, string> = {};
    if (searchObj.search_query) params.search = searchObj.search_query;
    if (searchObj.filters_json) {
      Object.entries(searchObj.filters_json).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== 'all') {
          params[k] = String(v);
        }
      });
    }
    onNavigateToIssues(params);
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
              onClick={() => onNavigateToIssues()}
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
              <Bookmark className="w-4 h-4" />
              <span>Saved Searches</span>
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
          Saved <span>Searches</span>
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1rem' }}>
          Automated search configurations monitored by our notification engine.
        </p>
      </section>

      {loading ? (
        <div style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <Loader2 className="w-8 h-8 animate-spin" style={{ margin: '0 auto 1rem auto' }} />
          <p>Loading saved searches...</p>
        </div>
      ) : error ? (
        <div className="card" style={{ padding: '2rem', textAlign: 'center', color: '#f87171' }}>
          <AlertCircle className="w-8 h-8" style={{ margin: '0 auto 1rem auto' }} />
          <p>{error}</p>
        </div>
      ) : searches.length === 0 ? (
        <div className="card" style={{ padding: '4rem 2rem', textAlign: 'center' }}>
          <Search className="w-10 h-10 text-muted" style={{ margin: '0 auto 1.25rem auto' }} />
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.5rem' }}>
            No Saved Searches Yet
          </h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
            Save search filter configurations from the Smart Search page to get automatic
            notifications when matching issues land.
          </p>
          <button
            onClick={() => onNavigateToIssues()}
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
            Go to Smart Search
          </button>
        </div>
      ) : (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
            gap: '1.25rem',
          }}
        >
          {searches.map((s) => (
            <div
              key={s.id}
              className="card"
              style={{
                padding: '1.5rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
              }}
            >
              <div>
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: '0.75rem',
                  }}
                >
                  <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                    {s.name}
                  </h4>
                  <button
                    onClick={() => handleDelete(s.id)}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: '#f87171',
                      cursor: 'pointer',
                    }}
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                {s.search_query && (
                  <p
                    style={{
                      fontSize: '0.875rem',
                      color: 'var(--text-secondary)',
                      marginBottom: '0.75rem',
                      fontFamily: 'var(--font-mono)',
                    }}
                  >
                    Query: "{s.search_query}"
                  </p>
                )}

                <div
                  style={{
                    display: 'flex',
                    flexWrap: 'wrap',
                    gap: '0.375rem',
                    marginBottom: '1.25rem',
                  }}
                >
                  {Object.entries(s.filters_json || {}).map(([k, v]) => (
                    <span
                      key={k}
                      style={{
                        fontSize: '0.75rem',
                        padding: '0.125rem 0.5rem',
                        borderRadius: '0.25rem',
                        background: 'rgba(59, 130, 246, 0.15)',
                        color: '#93c5fd',
                        border: '1px solid rgba(59, 130, 246, 0.3)',
                      }}
                    >
                      {k}: {String(v)}
                    </span>
                  ))}
                </div>
              </div>

              <button
                onClick={() => handleRunSearch(s)}
                style={{
                  width: '100%',
                  padding: '0.5rem',
                  background: 'var(--accent-blue)',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '0.375rem',
                  fontWeight: 600,
                  fontSize: '0.875rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '0.375rem',
                }}
              >
                <Search className="w-4 h-4" /> Run Search
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
