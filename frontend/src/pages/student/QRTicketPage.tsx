import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import QRCode from 'qrcode';
import api from '@/lib/api';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { Sparkles, ArrowLeft, Printer, Calendar, Clock, MapPin, CheckCircle, ShieldCheck } from 'lucide-react';
import { formatDate, formatTime } from '@/lib/utils';

export const QRTicketPage: React.FC = () => {
  const { qrCode } = useParams<{ qrCode: string }>();
  const [ticketData, setTicketData] = useState<any>(null);
  const [qrDataUrl, setQrDataUrl] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!qrCode) return;
    setIsLoading(true);
    api
      .get(`/attendance/verify/${qrCode}`)
      .then((res) => {
        setTicketData(res.data);
        return QRCode.toDataURL(qrCode, {
          width: 320,
          margin: 2,
          color: {
            dark: '#101828',
            light: '#FFFFFF',
          },
        });
      })
      .then((url) => setQrDataUrl(url))
      .catch(() => setError('Unable to find or verify this ticket pass.'))
      .finally(() => setIsLoading(false));
  }, [qrCode]);

  const handlePrint = () => {
    window.print();
  };

  if (isLoading) {
    return <LoadingSpinner text="Generating high-resolution pass..." className="py-24" />;
  }

  if (error || !ticketData) {
    return (
      <div className="max-w-md mx-auto px-4 py-20 text-center">
        <h2 className="text-xl font-bold text-slate-800">Invalid Pass</h2>
        <p className="text-sm text-slate-500 mt-2">{error || 'Ticket not found.'}</p>
        <Link
          to="/my-registrations"
          className="mt-6 inline-flex items-center gap-2 px-5 py-2.5 bg-violet-600 text-white rounded-xl text-sm font-semibold"
        >
          <ArrowLeft className="w-4 h-4" /> Back to My Passes
        </Link>
      </div>
    );
  }

  const isAttended = ticketData.status === 'attended';

  return (
    <div className="max-w-md mx-auto px-4 py-12 space-y-6 animate-fadeIn">
      {/* Top Bar */}
      <div className="flex items-center justify-between no-print">
        <Link
          to="/my-registrations"
          className="inline-flex items-center gap-2 text-xs font-bold text-slate-500 hover:text-violet-600"
        >
          <ArrowLeft className="w-4 h-4" />
          My Passes
        </Link>
        <button
          onClick={handlePrint}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-200 bg-white text-xs font-bold text-slate-700 hover:bg-slate-50 shadow-sm"
        >
          <Printer className="w-3.5 h-3.5" />
          Print Pass
        </button>
      </div>

      {/* Ticket Card Container */}
      <div className="bg-white rounded-3xl border-2 border-slate-900 overflow-hidden shadow-2xl relative">
        {/* Ticket Header */}
        <div className="bg-slate-900 text-white p-6 relative">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-violet-500 to-cyan-400 flex items-center justify-center text-white">
                <Sparkles className="w-3.5 h-3.5" />
              </div>
              <span className="text-sm font-bold tracking-tight">CampusConnect</span>
            </div>
            <span
              className={`px-3 py-1 rounded-full text-[11px] font-black uppercase tracking-wider ${
                isAttended
                  ? 'bg-cyan-500 text-slate-950'
                  : 'bg-emerald-400 text-slate-950'
              }`}
            >
              {isAttended ? 'CHECKED IN' : 'VALID PASS'}
            </span>
          </div>

          <h2 className="text-xl font-black tracking-tight leading-snug">
            {ticketData.event_title}
          </h2>
        </div>

        {/* QR Section */}
        <div className="p-8 flex flex-col items-center justify-center bg-slate-50 border-b-2 border-dashed border-slate-200 relative">
          {/* Decorative Notch cutouts */}
          <div className="absolute -left-4 -bottom-4 w-8 h-8 rounded-full bg-slate-100 border border-slate-300 z-10" />
          <div className="absolute -right-4 -bottom-4 w-8 h-8 rounded-full bg-slate-100 border border-slate-300 z-10" />

          {qrDataUrl && (
            <div className="p-4 bg-white rounded-2xl shadow-md border border-slate-200">
              <img src={qrDataUrl} alt="QR Access Pass" className="w-56 h-56" />
            </div>
          )}

          <div className="mt-4 flex items-center gap-1.5 text-xs font-mono text-slate-400">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>Encrypted Token: {qrCode?.slice(0, 18)}...</span>
          </div>
        </div>

        {/* Event Schedule & Venue */}
        <div className="p-6 space-y-3 bg-white text-xs text-slate-600">
          <div className="flex items-center gap-2.5">
            <Calendar className="w-4 h-4 text-violet-600" />
            <span className="font-semibold text-slate-800">
              {formatDate(ticketData.event_date)}
            </span>
          </div>
          <div className="flex items-center gap-2.5">
            <Clock className="w-4 h-4 text-violet-600" />
            <span>Time: {formatTime(ticketData.event_time)}</span>
          </div>
          <div className="flex items-center gap-2.5">
            <MapPin className="w-4 h-4 text-violet-600" />
            <span>Venue: University Main Campus</span>
          </div>
        </div>

        {/* Ticket Footer */}
        <div className="px-6 py-4 bg-slate-100 border-t border-slate-200 text-center">
          <p className="text-[11px] text-slate-500 font-medium">
            Please present this QR code to the entrance gate staff for check-in.
          </p>
        </div>
      </div>
    </div>
  );
};
