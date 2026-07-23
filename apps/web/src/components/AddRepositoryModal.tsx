import React, { useState } from 'react';
import { addRepository } from '../services/api';
import { Repository } from '../types/repository';
import { AlertCircle, Github, Loader2, Plus, X } from 'lucide-react';

interface AddRepositoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (repo: Repository) => void;
}

export const AddRepositoryModal: React.FC<AddRepositoryModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [input, setInput] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed) {
      setError('Please enter a repository name or URL');
      return;
    }

    if (!trimmed.includes('/') && !trimmed.includes('github.com')) {
      setError('Please specify in owner/repository format (e.g. facebook/react)');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const newRepo = await addRepository(trimmed);
      setInput('');
      onSuccess(newRepo);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add repository');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.75)',
        backdropFilter: 'blur(8px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 100,
        padding: '1rem',
      }}
      onClick={onClose}
    >
      <div
        className="card"
        style={{
          maxWidth: '520px',
          width: '100%',
          padding: '2rem',
          position: 'relative',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
          border: '1px solid rgba(255, 255, 255, 0.15)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '1.25rem',
            right: '1.25rem',
            background: 'none',
            border: 'none',
            color: 'var(--text-muted)',
            cursor: 'pointer',
            padding: '0.25rem',
            borderRadius: '0.375rem',
            transition: 'all 0.2s',
          }}
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header */}
        <div
          style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}
        >
          <div
            style={{
              width: '2.5rem',
              height: '2.5rem',
              borderRadius: '0.75rem',
              background: 'rgba(59, 130, 246, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--accent-blue)',
            }}
          >
            <Github className="w-6 h-6" />
          </div>
          <div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Add GitHub Repository</h3>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
              Monitor issues and updates for open-source projects
            </p>
          </div>
        </div>

        {/* Error Banner */}
        {error && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              padding: '0.75rem 1rem',
              background: 'var(--status-error-bg)',
              border: '1px solid var(--status-error-border)',
              borderRadius: '0.5rem',
              color: 'var(--status-error-text)',
              fontSize: '0.875rem',
              marginBottom: '1.25rem',
            }}
          >
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '1.5rem' }}>
            <label
              style={{
                display: 'block',
                fontSize: '0.875rem',
                fontWeight: 600,
                marginBottom: '0.5rem',
                color: 'var(--text-primary)',
              }}
            >
              Repository Name or GitHub URL
            </label>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="e.g. facebook/react or https://github.com/fastapi/fastapi"
              disabled={loading}
              style={{
                width: '100%',
                padding: '0.75rem 1rem',
                backgroundColor: 'rgba(0, 0, 0, 0.4)',
                border: '1px solid var(--border-color)',
                borderRadius: '0.5rem',
                color: 'var(--text-primary)',
                fontFamily: 'var(--font-mono)',
                fontSize: '0.875rem',
                outline: 'none',
                transition: 'all 0.2s',
              }}
              onFocus={(e) => {
                e.target.style.borderColor = 'var(--accent-blue)';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = 'var(--border-color)';
              }}
            />
            <span
              style={{
                display: 'block',
                fontSize: '0.75rem',
                color: 'var(--text-muted)',
                marginTop: '0.375rem',
              }}
            >
              We will validate this repository directly against the GitHub API.
            </span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              style={{
                padding: '0.625rem 1.25rem',
                background: 'transparent',
                border: '1px solid var(--border-color)',
                color: 'var(--text-secondary)',
                borderRadius: '0.5rem',
                fontWeight: 500,
                cursor: loading ? 'not-allowed' : 'pointer',
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
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
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: loading ? 0.7 : 1,
              }}
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Validating...</span>
                </>
              ) : (
                <>
                  <Plus className="w-4 h-4" />
                  <span>Add Repository</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
