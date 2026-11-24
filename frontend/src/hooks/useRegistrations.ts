import { useState, useEffect, useCallback } from 'react';
import api from '@/lib/api';
import type { Registration } from '@/types';

export function useRegistrations() {
  const [registrations, setRegistrations] = useState<Registration[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRegistrations = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.get<Registration[]>('/registrations/my');
      setRegistrations(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch registrations');
      setRegistrations([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRegistrations();
  }, [fetchRegistrations]);

  const registerForEvent = useCallback(async (eventId: number) => {
    const res = await api.post<Registration>('/registrations', { event_id: eventId });
    await fetchRegistrations();
    return res.data;
  }, [fetchRegistrations]);

  const cancelRegistration = useCallback(async (eventId: number) => {
    await api.delete(`/registrations/${eventId}`);
    await fetchRegistrations();
  }, [fetchRegistrations]);

  return { registrations, isLoading, error, registerForEvent, cancelRegistration, refetch: fetchRegistrations };
}
