import { useState, useEffect, useCallback } from 'react';
import api from '@/lib/api';
import type { Event, EventFilters, PaginatedResponse } from '@/types';

export function useEvents(initialFilters?: EventFilters) {
  const [events, setEvents] = useState<Event[]>([]);
  const [total, setTotal] = useState(0);
  const [pages, setPages] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<EventFilters>(initialFilters || { page: 1, limit: 12 });

  const fetchEvents = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params: Record<string, string | number | boolean> = {};
      if (filters.search) params.search = filters.search;
      if (filters.category && filters.category !== 'all') params.category = filters.category;
      if (filters.date_from) params.date_from = filters.date_from;
      if (filters.date_to) params.date_to = filters.date_to;
      if (filters.is_active !== undefined) params.is_active = filters.is_active;
      params.page = filters.page || 1;
      params.limit = filters.limit || 12;

      const res = await api.get<any>('/events', { params });
      const eventList = res.data.events || res.data.items || (Array.isArray(res.data) ? res.data : []);
      setEvents(eventList);
      setTotal(res.data.total ?? eventList.length);
      setPages(res.data.total_pages ?? res.data.pages ?? 1);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch events');
      // If paginated response fails, try plain array
      try {
        const res = await api.get<Event[]>('/events');
        setEvents(res.data);
        setTotal(res.data.length);
        setPages(1);
      } catch {
        setEvents([]);
      }
    } finally {
      setIsLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  const updateFilters = useCallback((newFilters: Partial<EventFilters>) => {
    setFilters((prev) => ({ ...prev, ...newFilters, page: newFilters.page || 1 }));
  }, []);

  return { events, total, pages, isLoading, error, filters, updateFilters, refetch: fetchEvents };
}
