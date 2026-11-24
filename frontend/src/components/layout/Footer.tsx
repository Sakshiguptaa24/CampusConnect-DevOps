import React from 'react';
import { Sparkles, Heart } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-slate-900 text-slate-400 py-12 border-t border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand */}
          <div className="space-y-4 md:col-span-2">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-violet-500 to-cyan-400 flex items-center justify-center text-white">
                <Sparkles className="w-4 h-4" />
              </div>
              <span className="text-lg font-bold text-white tracking-tight">
                Campus<span className="text-violet-400">Connect</span>
              </span>
            </div>
            <p className="text-sm text-slate-400 max-w-sm leading-relaxed">
              Smart collegiate event discovery, automated registration, QR ticketing, and real-time attendance tracking for modern universities.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-4">
              Explore
            </h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/events" className="hover:text-violet-400 transition-colors">
                  All Events
                </Link>
              </li>
              <li>
                <Link to="/dashboard" className="hover:text-violet-400 transition-colors">
                  Student Dashboard
                </Link>
              </li>
              <li>
                <Link to="/my-registrations" className="hover:text-violet-400 transition-colors">
                  My Tickets
                </Link>
              </li>
            </ul>
          </div>

          {/* System Info */}
          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-4">
              Platform
            </h4>
            <ul className="space-y-2 text-sm text-slate-400">
              <li>FastAPI + React SaaS</li>
              <li>Enterprise QR Verification</li>
              <li>Autonomous Waitlist Engine</li>
              <li>Prometheus Metrics Ready</li>
            </ul>
          </div>
        </div>

        <div className="pt-8 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs">
          <p>© {new Date().getFullYear()} CampusConnect. All rights reserved.</p>
          <p className="flex items-center gap-1">
            Engineered with <Heart className="w-3.5 h-3.5 text-rose-500 fill-rose-500" /> for modern campuses
          </p>
        </div>
      </div>
    </footer>
  );
};
