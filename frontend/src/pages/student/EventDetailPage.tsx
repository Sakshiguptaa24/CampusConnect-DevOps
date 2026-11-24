import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { useRegistrations } from '@/hooks/useRegistrations';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { Badge } from '@/components/shared/Badge';
import { ConfirmDialog } from '@/components/shared/ConfirmDialog';
import type { Event, Registration } from '@/types';
import {
  Calendar,
  Clock,
  MapPin,
  Users,
  ArrowLeft,
  CheckCircle2,
  AlertTriangle,
  QrCode,
  Share2,
} from 'lucide-react';
import { formatDate, formatTime, getCategoryIcon } from '@/lib/utils';

export const EventDetailPage: React.FC = () => {
  const { eventId } = useParams<{ eventId: string }>();
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuth();
  const { registerForEvent, cancelRegistration } = useRegistrations();

  const [event, setEvent] = useState<Event | null>(null);
  const [existingReg, setExistingReg] = useState<Registration | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [cancelModalOpen, setCancelModalOpen] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const fetchEventData = async () => {
    if (!eventId) return;
    setIsLoading(true);
    try {
      const res = await api.get<Event>(`/events/${eventId}`);
      setEvent(res.data);

      if (isAuthenticated) {
        const regsRes = await api.get<any[]>('/registrations/my');
        const userReg = regsRes.data.find(
          (r: any) => r.event_id === parseInt(eventId) && r.status !== 'cancelled'
        );
        setExistingReg(userReg || null);
      }
    } catch {
      setErrorMsg('Event could not be loaded.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchEventData();
  }, [eventId, isAuthenticated]);

  const handleRegister = async () => {
    if (!isAuthenticated) {
      navigate('/login', { state: { from: { pathname: `/events/${eventId}` } } });
      return;
    }
    if (!event) return;

    setIsSubmitting(true);
    setErrorMsg(null);
    try {
      const newReg = await registerForEvent(event.id);
      navigate(`/registration/confirm/${newReg.id}`, { state: { event, registration: newReg } });
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Registration failed.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleConfirmCancel = async () => {
    if (!event) return;
    setIsSubmitting(true);
    setCancelModalOpen(false);
    try {
      await cancelRegistration(event.id);
      setExistingReg(null);
      await fetchEventData();
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Failed to cancel registration.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return <LoadingSpinner text="Fetching event details..." className="py-24" />;
  }

  if (!event) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-20 text-center">
        <h2 className="text-xl font-bold text-slate-800">Event Not Found</h2>
        <p className="text-sm text-slate-500 mt-2">The requested event does not exist or has ended.</p>
        <Link
          to="/events"
          className="mt-6 inline-flex items-center gap-2 px-5 py-2.5 bg-violet-600 text-white rounded-xl text-sm font-semibold"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Events
        </Link>
      </div>
    );
  }

  const isFull = event.registered_count >= event.capacity;
  const fillPercentage = Math.min(100, Math.round((event.registered_count / event.capacity) * 100));

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8 animate-fadeIn">
      {/* Navigation Breadcrumb */}
      <div>
        <Link
          to="/events"
          className="inline-flex items-center gap-2 text-xs font-bold text-slate-500 hover:text-violet-600 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Events Catalog
        </Link>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700 text-sm flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left 2 Cols: Event Info */}
        <div className="lg:col-span-2 space-y-8">
          {/* Hero Banner Image */}
          <div className="h-72 sm:h-96 w-full rounded-3xl overflow-hidden bg-slate-100 relative shadow-sm border border-slate-200/60">
            <img
              src={
                event.image_url ||
                'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&auto=format&fit=crop&q=80'
              }
              alt={event.title}
              className="w-full h-full object-cover"
            />
            <div className="absolute top-4 left-4">
              <span className="px-3.5 py-1.5 bg-white/95 backdrop-blur-md rounded-full text-xs font-bold text-slate-800 shadow-sm flex items-center gap-1.5">
                <span>{getCategoryIcon(event.category)}</span>
                <span>{event.category}</span>
              </span>
            </div>
          </div>

          {/* Title & Metadata */}
          <div className="space-y-4">
            <h1 className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight leading-tight">
              {event.title}
            </h1>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
              <div className="flex items-start gap-3 p-4 rounded-2xl bg-white border border-slate-200/80">
                <Calendar className="w-5 h-5 text-violet-600 mt-0.5" />
                <div>
                  <p className="text-xs font-bold text-slate-400 uppercase">Date & Schedule</p>
                  <p className="text-sm font-semibold text-slate-800 mt-0.5">
                    {formatDate(event.date)}
                  </p>
                  <p className="text-xs text-slate-500">
                    {formatTime(event.time)} {event.end_time ? `– ${formatTime(event.end_time)}` : ''}
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3 p-4 rounded-2xl bg-white border border-slate-200/80">
                <MapPin className="w-5 h-5 text-violet-600 mt-0.5" />
                <div>
                  <p className="text-xs font-bold text-slate-400 uppercase">Location & Venue</p>
                  <p className="text-sm font-semibold text-slate-800 mt-0.5">{event.location}</p>
                  <p className="text-xs text-slate-500">University Campus Ground</p>
                </div>
              </div>
            </div>

            {/* Description */}
            <div className="pt-4">
              <h2 className="text-lg font-bold text-slate-900 mb-3">About This Event</h2>
              <div className="text-sm text-slate-600 leading-relaxed space-y-3 whitespace-pre-line bg-white p-6 rounded-3xl border border-slate-200/80">
                {event.description}
              </div>
            </div>
          </div>
        </div>

        {/* Right 1 Col: Registration Action Card */}
        <div className="space-y-6">
          <div className="bg-white rounded-3xl border border-slate-200/80 p-6 shadow-lg shadow-slate-100 space-y-6 sticky top-24">
            <div className="space-y-1">
              <span className="text-xs font-bold text-violet-600 uppercase tracking-wider">
                Registration Status
              </span>
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-bold text-slate-900">
                  {existingReg
                    ? existingReg.status === 'confirmed'
                      ? 'You are Registered!'
                      : existingReg.status === 'waitlisted'
                      ? 'You are on Waitlist'
                      : 'Attended'
                    : isFull
                    ? 'Waitlist Open'
                    : 'Open for Registration'}
                </h3>
              </div>
            </div>

            {/* Capacity Meter */}
            <div className="space-y-2 pt-2 border-t border-slate-100">
              <div className="flex justify-between text-xs">
                <span className="text-slate-500">Confirmed Attendees</span>
                <span className="font-bold text-slate-800">
                  {event.registered_count} / {event.capacity}
                </span>
              </div>
              <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    fillPercentage >= 100
                      ? 'bg-amber-500'
                      : fillPercentage >= 80
                      ? 'bg-indigo-500'
                      : 'bg-emerald-500'
                  }`}
                  style={{ width: `${fillPercentage}%` }}
                />
              </div>
              <p className="text-[11px] text-slate-400">
                {isFull
                  ? 'Event has reached max capacity. New signups enter the priority waitlist.'
                  : `${event.capacity - event.registered_count} seats remaining before waitlist opens.`}
              </p>
            </div>

            {/* Action Buttons */}
            <div className="space-y-3 pt-2">
              {existingReg ? (
                <>
                  <Link
                    to={`/ticket/${existingReg.qr_code}`}
                    className="w-full py-3 px-4 rounded-2xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-bold text-sm shadow-md shadow-violet-200 flex items-center justify-center gap-2 transition-all active:scale-[0.98]"
                  >
                    <QrCode className="w-4 h-4" />
                    <span>View QR Entry Pass</span>
                  </Link>

                  {existingReg.status !== 'attended' && (
                    <button
                      type="button"
                      onClick={() => setCancelModalOpen(true)}
                      disabled={isSubmitting}
                      className="w-full py-2.5 px-4 rounded-xl text-rose-600 bg-rose-50 hover:bg-rose-100 font-bold text-xs transition-colors"
                    >
                      Cancel My Pass
                    </button>
                  )}
                </>
              ) : (
                <button
                  type="button"
                  onClick={handleRegister}
                  disabled={isSubmitting}
                  className={`w-full py-3.5 px-4 rounded-2xl font-bold text-sm text-white shadow-xl transition-all active:scale-[0.98] flex items-center justify-center gap-2 ${
                    isFull
                      ? 'bg-amber-600 hover:bg-amber-500 shadow-amber-200'
                      : 'bg-violet-600 hover:bg-violet-700 shadow-violet-200'
                  }`}
                >
                  <CheckCircle2 className="w-4 h-4" />
                  <span>{isFull ? 'Join Priority Waitlist' : 'Register for Event'}</span>
                </button>
              )}
            </div>

            {/* Feature Perks */}
            <div className="border-t border-slate-100 pt-4 space-y-2 text-xs text-slate-500">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                <span>Instant digital QR code ticket</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                <span>Auto-promoted if waitlisted</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                <span>Cancellation anytime with 1 click</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Confirmation Dialog */}
      <ConfirmDialog
        isOpen={cancelModalOpen}
        title="Cancel Event Registration?"
        message="Are you sure you want to cancel your pass? If you are confirmed, your seat will be automatically given to the next student waiting in the queue."
        confirmLabel="Yes, Cancel Registration"
        isDestructive={true}
        onConfirm={handleConfirmCancel}
        onCancel={() => setCancelModalOpen(false)}
      />
    </div>
  );
};
