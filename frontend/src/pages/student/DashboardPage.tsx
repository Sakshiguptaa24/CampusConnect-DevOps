import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { StatsCard } from '@/components/shared/StatsCard';
import { EmptyState } from '@/components/shared/EmptyState';
import {
  Ticket,
  CalendarCheck,
  Clock,
  CheckCircle2,
  Calendar,
  MapPin,
  ArrowRight,
  QrCode,
} from 'lucide-react';
import { formatDate, formatTime } from '@/lib/utils';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [registrations, setRegistrations] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    api
      .get('/registrations/my')
      .then((res) => setRegistrations(res.data))
      .catch(() => setRegistrations([]))
      .finally(() => setIsLoading(false));
  }, []);

  const confirmedCount = registrations.filter((r) => r.status === 'confirmed').length;
  const attendedCount = registrations.filter((r) => r.status === 'attended').length;
  const waitlistedCount = registrations.filter((r) => r.status === 'waitlisted').length;
  const totalCount = registrations.filter((r) => r.status !== 'cancelled').length;

  const upcomingPasses = registrations.filter(
    (r) => r.status === 'confirmed' || r.status === 'waitlisted'
  );

  if (isLoading) {
    return <LoadingSpinner text="Loading your dashboard..." className="py-24" />;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10 animate-fadeIn">
      {/* Welcome Hero */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200/80">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-violet-600">
            Student Portal
          </span>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight mt-1">
            Welcome back, {user?.full_name?.split(' ')[0] || 'Student'}! 👋
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Department of {user?.department || 'General Studies'} • {user?.email}
          </p>
        </div>

        <Link
          to="/events"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-700 text-white font-bold text-sm shadow-md shadow-violet-200 transition-all active:scale-95 self-start sm:self-auto"
        >
          <Calendar className="w-4 h-4" />
          <span>Discover New Events</span>
        </Link>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Active Passes"
          value={totalCount}
          subtitle="Non-cancelled"
          icon={Ticket}
          colorScheme="violet"
        />
        <StatsCard
          title="Confirmed Seats"
          value={confirmedCount}
          subtitle="Guaranteed Entry"
          icon={CalendarCheck}
          colorScheme="emerald"
        />
        <StatsCard
          title="Waitlisted"
          value={waitlistedCount}
          subtitle="In queue"
          icon={Clock}
          colorScheme="amber"
        />
        <StatsCard
          title="Attended"
          value={attendedCount}
          subtitle="Verified check-ins"
          icon={CheckCircle2}
          colorScheme="cyan"
        />
      </div>

      {/* Upcoming Event Passes */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-slate-900">Your Upcoming Event Passes</h2>
          <Link
            to="/my-registrations"
            className="text-xs font-bold text-violet-600 hover:text-violet-700 inline-flex items-center gap-1"
          >
            <span>View All History</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {upcomingPasses.length === 0 ? (
          <EmptyState
            title="No upcoming event passes"
            description="You haven't registered for any upcoming events yet. Check out the schedule to secure your spots!"
            actionLabel="Browse Events"
            onAction={() => {}}
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {upcomingPasses.map((reg) => (
              <div
                key={reg.id}
                className="bg-white rounded-3xl border border-slate-200/80 p-6 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span
                      className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold ${
                        reg.status === 'confirmed'
                          ? 'bg-emerald-100 text-emerald-700'
                          : 'bg-amber-100 text-amber-700'
                      }`}
                    >
                      {reg.status === 'confirmed'
                        ? 'Confirmed Seat'
                        : `Waitlist #${reg.waitlist_position}`}
                    </span>
                    <span className="text-[11px] text-slate-400 font-mono">
                      #{reg.id}
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-slate-900 line-clamp-1 mb-2">
                    {reg.event_title}
                  </h3>

                  <div className="space-y-1.5 text-xs text-slate-500">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-3.5 h-3.5 text-violet-500" />
                      <span>{formatDate(reg.event_date)}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="w-3.5 h-3.5 text-violet-500" />
                      <span>{formatTime(reg.event_time)}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <MapPin className="w-3.5 h-3.5 text-violet-500" />
                      <span className="truncate">{reg.event_location}</span>
                    </div>
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-slate-100 flex items-center gap-2">
                  <Link
                    to={`/ticket/${reg.qr_code}`}
                    className="flex-1 py-2 px-3 rounded-xl bg-violet-50 hover:bg-violet-100 text-violet-700 font-bold text-xs flex items-center justify-center gap-1.5 transition-colors"
                  >
                    <QrCode className="w-3.5 h-3.5" />
                    <span>View QR Pass</span>
                  </Link>
                  <Link
                    to={`/events/${reg.event_id}`}
                    className="py-2 px-3 rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-600 font-semibold text-xs"
                  >
                    Details
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
