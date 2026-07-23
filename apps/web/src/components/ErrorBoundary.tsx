import { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught React Error:', error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            minHeight: '100vh',
            backgroundColor: '#090d16',
            color: '#f8fafc',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '2rem',
            fontFamily: 'Inter, sans-serif',
          }}
        >
          <div
            style={{
              maxWidth: '480px',
              width: '100%',
              backgroundColor: 'rgba(15, 23, 42, 0.8)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              borderRadius: '1rem',
              padding: '2.5rem',
              textAlign: 'center',
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5)',
            }}
          >
            <div
              style={{
                width: '4rem',
                height: '4rem',
                borderRadius: '50%',
                backgroundColor: 'rgba(239, 68, 68, 0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 1.5rem auto',
              }}
            >
              <AlertTriangle className="w-8 h-8 text-red-500" style={{ color: '#ef4444' }} />
            </div>

            <h2 style={{ fontSize: '1.5rem', fontWeight: 800, marginBottom: '0.75rem' }}>
              Something went wrong
            </h2>
            <p style={{ color: '#94a3b8', fontSize: '0.9375rem', marginBottom: '1.5rem' }}>
              An unexpected application error occurred. You can reload the page to restore your
              session.
            </p>

            {this.state.error && (
              <pre
                style={{
                  backgroundColor: 'rgba(0, 0, 0, 0.4)',
                  padding: '0.75rem',
                  borderRadius: '0.5rem',
                  color: '#f87171',
                  fontSize: '0.75rem',
                  textAlign: 'left',
                  overflowX: 'auto',
                  marginBottom: '1.5rem',
                }}
              >
                {this.state.error.message}
              </pre>
            )}

            <button
              onClick={this.handleReset}
              style={{
                width: '100%',
                padding: '0.75rem 1.5rem',
                backgroundColor: '#3b82f6',
                color: '#ffffff',
                border: 'none',
                borderRadius: '0.5rem',
                fontWeight: 700,
                fontSize: '0.9375rem',
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem',
              }}
            >
              <RefreshCw className="w-4 h-4" /> Reload Application
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
