import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '@/lib/api';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { EmptyState } from '@/components/shared/EmptyState';
import { ConfirmDialog } from '@/components/shared/ConfirmDialog';
import {
  Ticket,
  QrCode,
  Calendar,
  Clock,
  MapPin,
  XCircle,
  CheckCircle2,
  AlertTriangle,
} from 'lucide-react';
import { formatDate, formatTime } from '@/lib/utils';

export const MyRegistrationsPage: React.FC = () => {
  const [registrations, setRegistrations] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<'all' | 'confirmed' | 'waitlisted' | 'attended' | 'cancelled'>('all');
  const [isLoading, setIsLoading] = useState(true);
  const [cancelModalOpen, setCancelModalOpen] = useState(false);
  const [selectedReg, setSelectedReg] = useState<any>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const fetchRegistrations = () => {
    setIsLoading(true);
    api
      .get('/registrations/my')
      .then((res) => setRegistrations(res.data))
      .catch(() => setRegistrations([]))
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    fetchRegistrations();
  }, []);

  const handleCancelClick = (reg: any) => {
    setSelectedReg(reg);
    setCancelModalOpen(true);
  };

  const handleConfirmCancel = async () => {
    if (!selectedReg) return;
    setCancelModalOpen(false);
    setActionError(null);
    try {
      await api.delete(`/registrations/${selectedReg.event_id}`);
      fetchRegistrations();
    } catch (err: any) {
      setActionError(err.response?.data?.detail || 'Failed to cancel registration.');
    }
  };

  const filteredRegistrations = registrations.filter((reg) => {
    if (activeTab === 'all') return true;
    return reg.status === activeTab;
  });

  const tabCounts = {
    all: registrations.length,
    confirmed: registrations.filter((r) => r.status === 'confirmed').length,
    waitlisted: registrations.filter((r) => r.status === 'waitlisted').length,
    attended: registrations.filter((r) => r.status === 'attended').length,
    cancelled: registrations.filter((r) => r.status === 'cancelled').length,
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8 animate-fadeIn">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">My Event Passes</h1>
        <p className="text-sm text-slate-500 mt-1">
          Manage your confirmed registrations, waitlist status, and digital QR passes
        </p>
      </div>

      {actionError && (
        <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700 text-sm flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <span>{actionError}</span>
        </div>
      )}

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto border-b border-slate-200 pb-px">
        {(
          [
            { id: 'all', label: 'All Passes' },
            { id: 'confirmed', label: 'Confirmed' },
            { id: 'waitlisted', label: 'Waitlisted' },
            { id: 'attended', label: 'Attended' },
            { id: 'cancelled', label: 'Cancelled' },
          ] as const
        ).map((tab) => {
          const active = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`pb-3 px-4 text-xs font-bold transition-all relative whitespace-nowrap flex items-center gap-1.5 ${
                active
                  ? 'text-violet-600 border-b-2 border-violet-600'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              <span>{tab.label}</span>
              <span
                className={`text-[10px] px-1.5 py-0.2 rounded-full ${
                  active ? 'bg-violet-100 text-violet-700' : 'bg-slate-100 text-slate-600'
                }`}
              >
                {tabCounts[tab.id]}
              </span>
            </button>
          );
        })}
      </div>

      {/* Content Grid */}
      {isLoading ? (
        <LoadingSpinner text="Retrieving your passes..." className="py-20" />
      ) : filteredRegistrations.length === 0 ? (
        <EmptyState
          title={`No ${activeTab === 'all' ? '' : activeTab} passes`}
          description="You don't have any passes in this category."
          actionLabel="Browse Events Catalog"
          onAction={() => {}}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredRegistrations.map((reg) => {
            const isConfirmed = reg.status === 'confirmed';
            const isWaitlisted = reg.status === 'waitlisted';
            const isAttended = reg.status === 'attended';
            const isCancelled = reg.status === 'cancelled';

            return (
              <div
                key={reg.id}
                className="bg-white rounded-3xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-bold tracking-wide uppercase ${
                        isConfirmed
                          ? 'bg-emerald-100 text-emerald-700'
                          : isWaitlisted
                          ? 'bg-amber-100 text-amber-700'
                          : isAttended
                          ? 'bg-cyan-100 text-cyan-700'
                          : 'bg-rose-100 text-rose-700'
                      }`}
                    >
                      {isWaitlisted ? `WAITLIST #${reg.waitlist_position}` : reg.status}
                    </span>
                    <span className="text-[11px] font-mono text-slate-400">
                      ID: {reg.id}
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-slate-900 line-clamp-1 mb-3">
                    {reg.event_title}
                  </h3>

                  <div className="space-y-2 text-xs text-slate-500">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-3.5 h-3.5 text-violet-500" />
                      <span>{formatDate(reg.event_date)}</span>
                      <span className="text-slate-300">•</span>
                      <Clock className="w-3.5 h-3.5 text-violet-500" />
                      <span>{formatTime(reg.event_time)}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <MapPin className="w-3.5 h-3.5 text-violet-500" />
                      <span className="truncate">{reg.event_location}</span>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="mt-6 pt-4 border-t border-slate-100 flex items-center gap-2">
                  {!isCancelled && (
                    <Link
                      to={`/ticket/${reg.qr_code}`}
                      className="flex-1 py-2 px-3 rounded-xl bg-violet-600 hover:bg-violet-700 text-white font-bold text-xs flex items-center justify-center gap-1.5 transition-colors shadow-sm"
                    >
                      <QrCode className="w-3.5 h-3.5" />
                      <span>View Pass</span>
                    </Link>
                  )}

                  {!isCancelled && !isAttended && (
                    <button
                      onClick={() => handleCancelClick(reg)}
                      className="py-2 px-3 rounded-xl bg-slate-100 hover:bg-rose-50 hover:text-rose-600 text-slate-600 font-semibold text-xs transition-colors"
                    >
                      Cancel
                    </button>
                  )}

                  {isCancelled && (
                    <Link
                      to={`/events/${reg.event_id}`}
                      className="w-full py-2 px-3 rounded-xl bg-slate-100 hover:bg-violet-50 text-slate-700 hover:text-violet-700 font-bold text-xs text-center transition-colors"
                    >
                      Re-register for Event
                    </Link>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Cancel Confirmation Dialog */}
      <ConfirmDialog
        isOpen={cancelModalOpen}
        title="Cancel Pass?"
        message={`Are you sure you want to cancel your pass for "${selectedReg?.event_title}"? Your spot will be released immediately.`}
        confirmLabel="Yes, Cancel Pass"
        isDestructive={true}
        onConfirm={handleConfirmCancel}
        onCancel={() => setCancelModalOpen(false)}
      />
    </div>
  );
};
