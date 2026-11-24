import React, { useState } from 'react';
import api from '@/lib/api';
import {
  QrCode,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Scan,
  User,
  Calendar,
  Clock,
  ArrowRight,
} from 'lucide-react';
import { formatDate, formatTime } from '@/lib/utils';

export const AttendanceManagementPage: React.FC = () => {
  const [qrInput, setQrInput] = useState('');
  const [isVerifying, setIsVerifying] = useState(false);
  const [result, setResult] = useState<{
    status: 'success' | 'error' | 'already_marked';
    message: string;
    data?: any;
  } | null>(null);

  const [recentScans, setRecentScans] = useState<any[]>([]);

  const handleScanSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!qrInput.trim()) return;

    setIsVerifying(true);
    setResult(null);

    try {
      // 1. Verify and mark attended
      const res = await api.post('/attendance/verify', { qr_code: qrInput.trim() });
      const scanData = res.data;

      setResult({
        status: 'success',
        message: 'Attendee Checked In Successfully! Entry Granted.',
        data: scanData,
      });

      // Add to recent scans list
      setRecentScans((prev) => [
        {
          id: Date.now(),
          qr_code: qrInput.trim(),
          event_title: scanData.event_title || 'Campus Event',
          time: new Date().toLocaleTimeString(),
          status: 'verified',
        },
        ...prev.slice(0, 9),
      ]);

      setQrInput('');
    } catch (err: any) {
      const errorMsg =
        err.response?.data?.detail || 'Invalid QR ticket or pass verification failed.';
      const isAlready = errorMsg.toLowerCase().includes('already');

      setResult({
        status: isAlready ? 'already_marked' : 'error',
        message: errorMsg,
      });
    } finally {
      setIsVerifying(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fadeIn">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-black text-slate-900 tracking-tight">
          QR Check-In & Gate Verification
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Scan attendee QR passes or enter ticket UUIDs to grant entry and prevent duplicate access
        </p>
      </div>

      {/* Main Scanner Box */}
      <div className="bg-white rounded-3xl border border-slate-200/80 p-8 shadow-sm text-center">
        <div className="w-16 h-16 rounded-2xl bg-violet-100 text-violet-600 flex items-center justify-center mx-auto mb-4 shadow-sm">
          <Scan className="w-8 h-8 animate-pulse" />
        </div>

        <h2 className="text-lg font-bold text-slate-900 mb-1">Gate Check-In Terminal</h2>
        <p className="text-xs text-slate-500 max-w-md mx-auto mb-6">
          Use a handheld barcode/QR scanner or manually paste the student pass token below
        </p>

        <form onSubmit={handleScanSubmit} className="max-w-md mx-auto flex gap-2">
          <div className="relative flex-1">
            <QrCode className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              value={qrInput}
              onChange={(e) => setQrInput(e.target.value)}
              placeholder="Paste or scan QR code string..."
              autoFocus
              className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-2xl text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-violet-500 font-mono shadow-inner"
            />
          </div>
          <button
            type="submit"
            disabled={isVerifying || !qrInput.trim()}
            className="px-6 py-3 bg-violet-600 hover:bg-violet-700 text-white font-bold text-xs rounded-2xl shadow-md shadow-violet-200 transition-all disabled:opacity-50 active:scale-95 flex items-center gap-1.5"
          >
            <span>{isVerifying ? 'Verifying...' : 'Verify Pass'}</span>
          </button>
        </form>

        {/* Scan Result Feedback Card */}
        {result && (
          <div
            className={`mt-6 p-6 rounded-2xl text-left border max-w-md mx-auto animate-fadeIn ${
              result.status === 'success'
                ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
                : result.status === 'already_marked'
                ? 'bg-amber-50 border-amber-200 text-amber-900'
                : 'bg-rose-50 border-rose-200 text-rose-900'
            }`}
          >
            <div className="flex items-start gap-3">
              {result.status === 'success' ? (
                <CheckCircle2 className="w-6 h-6 text-emerald-600 flex-shrink-0 mt-0.5" />
              ) : result.status === 'already_marked' ? (
                <AlertTriangle className="w-6 h-6 text-amber-600 flex-shrink-0 mt-0.5" />
              ) : (
                <XCircle className="w-6 h-6 text-rose-600 flex-shrink-0 mt-0.5" />
              )}
              <div>
                <h4 className="font-black text-sm">
                  {result.status === 'success'
                    ? 'VERIFIED: ACCESS GRANTED'
                    : result.status === 'already_marked'
                    ? 'DUPLICATE: ALREADY CHECKED IN'
                    : 'ACCESS REJECTED'}
                </h4>
                <p className="text-xs mt-1 opacity-90 leading-relaxed">{result.message}</p>

                {result.data && (
                  <div className="mt-3 pt-3 border-t border-emerald-200 text-xs space-y-1">
                    <p>
                      <strong>Event:</strong> {result.data.event_title || 'Campus Event'}
                    </p>
                    <p>
                      <strong>Status:</strong> {result.data.status}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Live Recent Scans Audit Log */}
      <div className="bg-white rounded-3xl border border-slate-200/80 p-6 shadow-sm">
        <h3 className="text-base font-bold text-slate-900 mb-4">Gate Check-In Stream</h3>

        {recentScans.length === 0 ? (
          <p className="text-xs text-slate-400 py-6 text-center">
            No passes scanned yet in this session.
          </p>
        ) : (
          <div className="divide-y divide-slate-100">
            {recentScans.map((scan) => (
              <div key={scan.id} className="py-3 flex items-center justify-between text-xs">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center">
                    <CheckCircle2 className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="font-bold text-slate-900">{scan.event_title}</p>
                    <p className="text-slate-400 font-mono text-[11px] truncate max-w-xs">
                      {scan.qr_code}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <span className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 font-bold text-[10px]">
                    APPROVED
                  </span>
                  <p className="text-slate-400 text-[10px] mt-0.5">{scan.time}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
