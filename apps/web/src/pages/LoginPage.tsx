import React from 'react';
import { useAuth } from '../hooks/useAuth';
import { Github, Shield, Sparkles, Terminal, Zap } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const { loginWithGithub } = useAuth();

  return (
    <div
      style={{
        minHeight: '85vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem 1rem',
      }}
    >
      <div
        className="card"
        style={{
          maxWidth: '480px',
          width: '100%',
          padding: '2.5rem',
          textAlign: 'center',
          boxShadow: '0 20px 40px rgba(0, 0, 0, 0.4)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
        }}
      >
        {/* Brand Header */}
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '3.5rem',
            height: '3.5rem',
            background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))',
            borderRadius: '1rem',
            marginBottom: '1.5rem',
            boxShadow: '0 8px 20px rgba(59, 130, 246, 0.4)',
          }}
        >
          <Zap className="w-7 h-7 text-white" />
        </div>

        <h1
          style={{
            fontSize: '2rem',
            fontWeight: 800,
            marginBottom: '0.75rem',
            letterSpacing: '-0.025em',
          }}
        >
          IssueRadar <span style={{ color: 'var(--accent-blue)' }}>AI</span>
        </h1>

        <p
          style={{
            color: 'var(--text-secondary)',
            fontSize: '0.95rem',
            lineHeight: 1.6,
            marginBottom: '2rem',
          }}
        >
          The intelligent platform empowering open-source contributors to discover, prioritize, and
          fix high-impact GitHub issues.
        </p>

        {/* Feature Highlights */}
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '0.75rem',
            textAlign: 'left',
            marginBottom: '2.25rem',
            padding: '1rem 1.25rem',
            background: 'rgba(255, 255, 255, 0.02)',
            borderRadius: '0.75rem',
            border: '1px solid var(--border-color)',
          }}
        >
          <div
            style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.875rem' }}
          >
            <Sparkles className="w-4 h-4 text-cyan-400" />
            <span>AI-Driven Issue Skill Matching</span>
          </div>
          <div
            style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.875rem' }}
          >
            <Terminal className="w-4 h-4 text-purple-400" />
            <span>Real-time GitHub Repository Scanning</span>
          </div>
          <div
            style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.875rem' }}
          >
            <Shield className="w-4 h-4 text-emerald-400" />
            <span>Secure Fernet Token Encryption & HttpOnly Sessions</span>
          </div>
        </div>

        {/* GitHub OAuth Button */}
        <button
          onClick={loginWithGithub}
          style={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.75rem',
            padding: '0.875rem 1.5rem',
            backgroundColor: '#24292e',
            color: '#ffffff',
            border: '1px solid rgba(255, 255, 255, 0.15)',
            borderRadius: '0.75rem',
            fontSize: '1rem',
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'all 0.2s ease-in-out',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.backgroundColor = '#2f363d';
            e.currentTarget.style.borderColor = 'var(--accent-blue)';
            e.currentTarget.style.transform = 'translateY(-1px)';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.backgroundColor = '#24292e';
            e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.15)';
            e.currentTarget.style.transform = 'translateY(0)';
          }}
        >
          <Github className="w-5 h-5" />
          <span>Continue with GitHub</span>
        </button>

        <p
          style={{
            marginTop: '1.25rem',
            fontSize: '0.75rem',
            color: 'var(--text-muted)',
          }}
        >
          By logging in, you authorize IssueRadar AI to verify your GitHub identity.
        </p>
      </div>
    </div>
  );
};
