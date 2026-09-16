import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import type { SystemStatus } from '@/types';

export function useSystemStatus() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    const fetchStatus = async () => {
      try {
        const data = await api.getSystemStatus();
        if (mounted) {
          setStatus(data);
          setIsLoading(false);
        }
      } catch (err) {
        console.error('Failed to fetch system status', err);
        // Fallback or just ignore, to keep UI from breaking
        if (mounted && !status) setIsLoading(false);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 30000);

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return { status, isLoading };
}
