import React, { useEffect, useState } from 'react';
import { useParams, Link, useLocation } from 'react-router-dom';
import QRCode from 'qrcode';
import { CheckCircle2, Clock, QrCode, ArrowRight, Calendar, MapPin } from 'lucide-react';
import { formatDate, formatTime } from '@/lib/utils';
import api from '@/lib/api';

export const RegistrationConfirmPage: React.FC = () => {
  const { regId } = useParams<{ regId: string }>();
  const location = useLocation();

  const stateData = (location.state as any) || {};
  const [event, setEvent] = useState<any>(stateData.event || null);
  const [registration, setRegistration] = useState<any>(stateData.registration || null);
  const [qrDataUrl, setQrDataUrl] = useState<string>('');

  useEffect(() => {
    // If state data wasn't passed directly, fetch from user registrations
    if (!registration && regId) {
      api.get('/registrations/my').then((res) => {
        const found = res.data.find((r: any) => r.id === parseInt(regId));
        if (found) {
          setRegistration(found);
          setEvent({
            title: found.event_title,
            date: found.event_date,
            time: found.event_time,
            location: found.event_location,
          });
        }
      });
    }
  }, [regId, registration]);

  useEffect(() => {
    if (registration?.qr_code) {
      QRCode.toDataURL(registration.qr_code, {
        width: 256,
        margin: 2,
        color: {
          dark: '#101828',
          light: '#FFFFFF',
        },
      })
        .then((url) => setQrDataUrl(url))
        .catch(console.error);
    }
  }, [registration]);

  const isWaitlisted = registration?.status === 'waitlisted';

  return (
    <div className="max-w-2xl mx-auto px-4 py-16 text-center animate-fadeIn">
      {/* Icon badge */}
      <div
        className={`w-20 h-20 rounded-3xl mx-auto flex items-center justify-center mb-6 shadow-xl ${
          isWaitlisted
            ? 'bg-amber-100 text-amber-600 shadow-amber-100'
            : 'bg-emerald-100 text-emerald-600 shadow-emerald-100'
        }`}
      >
        {isWaitlisted ? <Clock className="w-10 h-10" /> : <CheckCircle2 className="w-10 h-10" />}
      </div>

      <h1 className="text-3xl font-black text-slate-900 tracking-tight">
        {isWaitlisted ? 'Added to Priority Waitlist!' : 'Registration Confirmed!'}
      </h1>

      <p className="mt-2 text-sm text-slate-600 max-w-md mx-auto">
        {isWaitlisted
          ? `You are in position #${registration?.waitlist_position} on the queue. If a confirmed attendee cancels, your pass will be promoted automatically.`
          : 'Your digital pass is generated. Present this QR code at the check-in desk on event day.'}
      </p>

      {/* Ticket Card Preview */}
      <div className="mt-8 bg-white rounded-3xl border border-slate-200 p-8 shadow-xl text-left max-w-md mx-auto">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              CampusConnect Pass
            </span>
            <h3 className="text-base font-bold text-slate-900 line-clamp-1">
              {event?.title || 'Event Registration'}
            </h3>
          </div>
          <span
            className={`px-2.5 py-1 rounded-full text-xs font-bold ${
              isWaitlisted ? 'bg-amber-100 text-amber-700' : 'bg-emerald-100 text-emerald-700'
            }`}
          >
            {registration?.status?.toUpperCase()}
          </span>
        </div>

        {/* QR Code */}
        {qrDataUrl && (
          <div className="py-6 flex flex-col items-center justify-center bg-slate-50/50 rounded-2xl my-4 border border-dashed border-slate-200">
            <img src={qrDataUrl} alt="Event QR Ticket" className="w-44 h-44 rounded-xl shadow-sm" />
            <span className="mt-2 text-[10px] font-mono text-slate-400">
              Pass ID: {registration?.qr_code?.slice(0, 16)}...
            </span>
          </div>
        )}

        <div className="space-y-2 text-xs text-slate-600 pt-2">
          {event?.date && (
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-violet-500" />
              <span>
                {formatDate(event.date)} at {formatTime(event.time)}
              </span>
            </div>
          )}
          {event?.location && (
            <div className="flex items-center gap-2">
              <MapPin className="w-4 h-4 text-violet-500" />
              <span>{event.location}</span>
            </div>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
        {registration?.qr_code && (
          <Link
            to={`/ticket/${registration.qr_code}`}
            className="w-full sm:w-auto px-6 py-3 rounded-xl bg-violet-600 hover:bg-violet-700 text-white font-bold text-sm shadow-md shadow-violet-200 flex items-center justify-center gap-2 transition-all"
          >
            <QrCode className="w-4 h-4" />
            <span>Open Full QR Ticket</span>
          </Link>
        )}
        <Link
          to="/dashboard"
          className="w-full sm:w-auto px-6 py-3 rounded-xl bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 font-bold text-sm transition-all"
        >
          Go to Student Dashboard
        </Link>
      </div>
    </div>
  );
};
