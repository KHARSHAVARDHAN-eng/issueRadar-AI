import React from 'react';

export const IssueSkeleton: React.FC = () => {
  return (
    <div
      className="card"
      style={{
        padding: '1.25rem 1.5rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        opacity: 0.6,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexGrow: 1 }}>
        <div
          style={{
            width: '1.25rem',
            height: '1.25rem',
            borderRadius: '50%',
            backgroundColor: 'var(--border-color)',
          }}
        />
        <div style={{ flexGrow: 1 }}>
          <div
            style={{
              width: '60%',
              height: '1.125rem',
              backgroundColor: 'var(--border-color)',
              borderRadius: '0.375rem',
              marginBottom: '0.5rem',
            }}
          />
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <div
              style={{
                width: '4rem',
                height: '0.875rem',
                backgroundColor: 'var(--border-color)',
                borderRadius: '9999px',
              }}
            />
            <div
              style={{
                width: '5rem',
                height: '0.875rem',
                backgroundColor: 'var(--border-color)',
                borderRadius: '9999px',
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
