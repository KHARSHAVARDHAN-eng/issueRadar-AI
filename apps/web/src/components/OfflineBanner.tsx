import React, { useEffect, useState } from 'react';
import { WifiOff } from 'lucide-react';

export const OfflineBanner: React.FC = () => {
  const [isOffline, setIsOffline] = useState<boolean>(!navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOffline(false);
    const handleOffline = () => setIsOffline(true);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (!isOffline) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        backgroundColor: '#ef4444',
        color: '#ffffff',
        padding: '0.5rem 1rem',
        textAlign: 'center',
        fontWeight: 600,
        fontSize: '0.875rem',
        zIndex: 9999,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '0.5rem',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.2)',
      }}
    >
      <WifiOff className="w-4 h-4" />
      <span>Network Connection Lost — You are operating in offline mode.</span>
    </div>
  );
};
