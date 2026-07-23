import React, { useEffect, useState } from 'react';
import { ProtectedRoute } from './components/ProtectedRoute';
import { AuthProvider } from './context/AuthContext';
import { BookmarksPage } from './pages/BookmarksPage';
import { DashboardPage } from './pages/DashboardPage';
import { IssuesPage } from './pages/IssuesPage';
import { JobsPage } from './pages/JobsPage';
import { LoginPage } from './pages/LoginPage';
import { NotificationsPage } from './pages/NotificationsPage';
import { RepositoriesPage } from './pages/RepositoriesPage';
import { SavedSearchesPage } from './pages/SavedSearchesPage';
import { fetchNotifications } from './services/api';

export const AppContent: React.FC = () => {
  const [currentView, setCurrentView] = useState<
    | 'dashboard'
    | 'repositories'
    | 'issues'
    | 'saved-searches'
    | 'bookmarks'
    | 'notifications'
    | 'jobs'
  >('dashboard');
  const [unreadNotifCount, setUnreadNotifCount] = useState<number>(0);

  // Poll unread notifications count
  useEffect(() => {
    const checkNotifications = async () => {
      try {
        const notifs = await fetchNotifications(true);
        setUnreadNotifCount(notifs.filter((n) => !n.is_read).length);
      } catch (err) {
        // Unauthenticated or network error
      }
    };
    checkNotifications();
    const interval = setInterval(checkNotifications, 15000);
    return () => clearInterval(interval);
  }, []);

  const renderView = () => {
    switch (currentView) {
      case 'repositories':
        return (
          <RepositoriesPage
            onNavigateToDashboard={() => setCurrentView('dashboard')}
            onNavigateToIssues={() => setCurrentView('issues')}
          />
        );
      case 'issues':
        return (
          <IssuesPage
            onNavigateToDashboard={() => setCurrentView('dashboard')}
            onNavigateToRepositories={() => setCurrentView('repositories')}
          />
        );
      case 'saved-searches':
        return (
          <SavedSearchesPage
            onNavigateToDashboard={() => setCurrentView('dashboard')}
            onNavigateToRepositories={() => setCurrentView('repositories')}
            onNavigateToIssues={() => setCurrentView('issues')}
          />
        );
      case 'bookmarks':
        return (
          <BookmarksPage
            onNavigateToDashboard={() => setCurrentView('dashboard')}
            onNavigateToRepositories={() => setCurrentView('repositories')}
            onNavigateToIssues={() => setCurrentView('issues')}
          />
        );
      case 'notifications':
        return (
          <NotificationsPage
            onNavigateToDashboard={() => setCurrentView('dashboard')}
            onNavigateToRepositories={() => setCurrentView('repositories')}
            onNavigateToIssues={() => setCurrentView('issues')}
          />
        );
      case 'jobs':
        return (
          <JobsPage
            onNavigateToDashboard={() => setCurrentView('dashboard')}
            onNavigateToRepositories={() => setCurrentView('repositories')}
            onNavigateToIssues={() => setCurrentView('issues')}
          />
        );
      default:
        return (
          <DashboardPage
            onNavigateToRepositories={() => setCurrentView('repositories')}
            onNavigateToIssues={() => setCurrentView('issues')}
            onNavigateToSavedSearches={() => setCurrentView('saved-searches')}
            onNavigateToBookmarks={() => setCurrentView('bookmarks')}
            onNavigateToNotifications={() => setCurrentView('notifications')}
            onNavigateToJobs={() => setCurrentView('jobs')}
          />
        );
    }
  };

  return (
    <div>
      {/* Global Unread Notification Floating Badge Header indicator */}
      {unreadNotifCount > 0 && currentView !== 'notifications' && (
        <div
          onClick={() => setCurrentView('notifications')}
          style={{
            position: 'fixed',
            bottom: '1.5rem',
            right: '1.5rem',
            zIndex: 99,
            backgroundColor: 'var(--accent-blue)',
            color: '#fff',
            padding: '0.625rem 1rem',
            borderRadius: '9999px',
            boxShadow: '0 10px 25px -5px rgba(59, 130, 246, 0.5)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            fontWeight: 700,
            fontSize: '0.875rem',
            cursor: 'pointer',
          }}
        >
          <span>🔔 {unreadNotifCount} New Alerts</span>
        </div>
      )}

      {renderView()}
    </div>
  );
};

export const App: React.FC = () => {
  const isLoginPage = window.location.pathname === '/login';

  if (isLoginPage) {
    return <LoginPage />;
  }

  return (
    <AuthProvider>
      <ProtectedRoute>
        <AppContent />
      </ProtectedRoute>
    </AuthProvider>
  );
};

export default App;
