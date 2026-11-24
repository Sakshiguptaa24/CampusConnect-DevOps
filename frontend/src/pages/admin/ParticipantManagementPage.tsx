import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from '@/lib/api';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { EmptyState } from '@/components/shared/EmptyState';
import { Users, FileDown, Search, CheckCircle2, Clock, XCircle, AlertCircle } from 'lucide-react';
import { formatDate } from '@/lib/utils';
import type { Event } from '@/types';

export const ParticipantManagementPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const selectedEventId = searchParams.get('eventId') || '';

  const [events, setEvents] = useState<Event[]>([]);
  const [participants, setParticipants] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [exportLoading, setExportLoading] = useState(false);

  useEffect(() => {
    api
      .get('/events?page=1&page_size=100')
      .then((res) => {
        const evs = res.data.events || res.data.items || [];
        setEvents(evs);
        if (!selectedEventId && evs.length > 0) {
          setSearchParams({ eventId: evs[0].id.toString() });
        }
      })
      .catch(console.error);
  }, []);

  useEffect(() => {
    if (!selectedEventId) return;
    setIsLoading(true);
    api
      .get(`/registrations/events/${selectedEventId}/participants`)
      .then((res) => setParticipants(res.data))
      .catch(() => setParticipants([]))
      .finally(() => setIsLoading(false));
  }, [selectedEventId]);

  const handleExportCSV = async () => {
    if (!selectedEventId) return;
    setExportLoading(true);
    try {
      const response = await api.get(`/admin/events/${selectedEventId}/export-csv`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `participants_event_${selectedEventId}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('Failed to export CSV');
    } finally {
      setExportLoading(false);
    }
  };

  const filteredParticipants = participants.filter(
    (p) =>
      p.user_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.user_email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.user_department?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const currentEvent = events.find((e) => e.id.toString() === selectedEventId);

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header & Event Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">Participant Roster</h1>
          <p className="text-xs text-slate-500 mt-1">
            Track confirmed registrations, waitlist standings, and export attendance records
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Event Picker Dropdown */}
          <select
            value={selectedEventId}
            onChange={(e) => setSearchParams({ eventId: e.target.value })}
            className="px-3 py-2 bg-white border border-slate-200 rounded-xl text-xs font-bold text-slate-800 focus:outline-none focus:ring-2 focus:ring-violet-500 shadow-sm"
          >
            {events.map((ev) => (
              <option key={ev.id} value={ev.id}>
                {ev.title} ({ev.registered_count}/{ev.capacity})
              </option>
            ))}
          </select>

          <button
            onClick={handleExportCSV}
            disabled={exportLoading || participants.length === 0}
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold shadow-md shadow-emerald-200 transition-all disabled:opacity-50"
          >
            <FileDown className="w-4 h-4" />
            <span>{exportLoading ? 'Exporting...' : 'Export CSV'}</span>
          </button>
        </div>
      </div>

      {/* Summary Chips */}
      {currentEvent && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
            <span className="text-xs text-slate-400">Total Registered</span>
            <p className="text-xl font-bold text-slate-900">{participants.length}</p>
          </div>
          <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
            <span className="text-xs text-slate-400">Confirmed Attendees</span>
            <p className="text-xl font-bold text-emerald-600">
              {participants.filter((p) => p.status === 'confirmed').length}
            </p>
          </div>
          <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
            <span className="text-xs text-slate-400">Waitlisted</span>
            <p className="text-xl font-bold text-amber-600">
              {participants.filter((p) => p.status === 'waitlisted').length}
            </p>
          </div>
          <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
            <span className="text-xs text-slate-400">Checked In (Attended)</span>
            <p className="text-xl font-bold text-cyan-600">
              {participants.filter((p) => p.status === 'attended').length}
            </p>
          </div>
        </div>
      )}

      {/* Search Input */}
      <div className="flex items-center gap-4 bg-white p-3 rounded-2xl border border-slate-200 shadow-sm">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search attendees by name, email, department..."
            className="w-full pl-9 pr-4 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-violet-500"
          />
        </div>
      </div>

      {/* Table */}
      {isLoading ? (
        <LoadingSpinner text="Fetching attendee rosters..." className="py-20" />
      ) : filteredParticipants.length === 0 ? (
        <EmptyState
          title="No participants found"
          description="There are currently no registered attendees for this event matching your query."
        />
      ) : (
        <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider font-semibold border-b border-slate-200">
                <tr>
                  <th className="py-3.5 px-4">Attendee Name</th>
                  <th className="py-3.5 px-4">Email</th>
                  <th className="py-3.5 px-4">Department</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-4">Registered Date</th>
                  <th className="py-3.5 px-4 text-right">QR Pass Token</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredParticipants.map((p) => (
                  <tr key={p.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="py-3.5 px-4 font-bold text-slate-900">{p.user_name}</td>
                    <td className="py-3.5 px-4 text-slate-600">{p.user_email}</td>
                    <td className="py-3.5 px-4 text-slate-600">{p.user_department || '—'}</td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                          p.status === 'confirmed'
                            ? 'bg-emerald-100 text-emerald-700'
                            : p.status === 'waitlisted'
                            ? 'bg-amber-100 text-amber-700'
                            : p.status === 'attended'
                            ? 'bg-cyan-100 text-cyan-700'
                            : 'bg-rose-100 text-rose-700'
                        }`}
                      >
                        {p.status === 'waitlisted' ? `WAITLIST #${p.waitlist_position}` : p.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-500">
                      {p.registered_at ? formatDate(p.registered_at) : '—'}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-[11px] text-slate-400 text-right">
                      {p.qr_code?.slice(0, 14)}...
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
