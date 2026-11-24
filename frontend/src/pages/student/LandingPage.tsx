import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '@/lib/api';
import type { Event } from '@/types';
import {
  Sparkles,
  Calendar,
  QrCode,
  Users,
  ShieldCheck,
  ArrowRight,
  Clock,
  MapPin,
  CheckCircle,
} from 'lucide-react';
import { formatDate, formatTime, getCategoryIcon } from '@/lib/utils';

export const LandingPage: React.FC = () => {
  const [featuredEvents, setFeaturedEvents] = useState<Event[]>([]);

  useEffect(() => {
    api
      .get('/events?page=1&page_size=3')
      .then((res) => {
        const items = res.data.events || res.data.items || (Array.isArray(res.data) ? res.data : []);
        setFeaturedEvents(items.slice(0, 3));
      })
      .catch(() => setFeaturedEvents([]));
  }, []);

  return (
    <div className="space-y-24 pb-20">
      {/* Hero Section */}
      <section className="relative pt-20 pb-16 overflow-hidden">
        {/* Background glow orbs */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[650px] h-[350px] bg-gradient-to-tr from-violet-500/15 via-indigo-500/10 to-cyan-500/15 blur-3xl rounded-full pointer-events-none" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-violet-50 border border-violet-200/80 text-violet-700 text-xs font-semibold mb-8 animate-fadeIn">
            <Sparkles className="w-3.5 h-3.5 text-violet-600" />
            <span>Next-Generation College Event Orchestration</span>
          </div>

          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-black text-slate-900 tracking-tight max-w-4xl mx-auto leading-[1.1]">
            Experience Campus Life.{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-600 via-indigo-600 to-cyan-500">
              Without the Hassle.
            </span>
          </h1>

          <p className="mt-6 text-lg sm:text-xl text-slate-600 max-w-2xl mx-auto font-normal leading-relaxed">
            Discover premier hackathons, tech summits, cultural fests, and workshops. Instant QR passes, automated waitlists, and zero queueing.
          </p>

          {/* CTA Buttons */}
          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/events"
              className="w-full sm:w-auto px-8 py-3.5 rounded-2xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-bold text-base shadow-xl shadow-violet-500/25 transition-all hover:scale-105 active:scale-95 flex items-center justify-center gap-2"
            >
              <span>Explore All Events</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              to="/login"
              className="w-full sm:w-auto px-8 py-3.5 rounded-2xl bg-white hover:bg-slate-50 text-slate-700 font-bold text-base border border-slate-200 shadow-sm transition-all hover:border-slate-300"
            >
              Sign In to Your Pass
            </Link>
          </div>

          {/* Social Proof Stats */}
          <div className="mt-16 pt-12 border-t border-slate-200/60 max-w-4xl mx-auto grid grid-cols-2 sm:grid-cols-4 gap-6 text-center">
            <div>
              <p className="text-3xl font-black text-slate-900">100%</p>
              <p className="text-xs font-medium text-slate-500 mt-0.5">Automated Waitlist</p>
            </div>
            <div>
              <p className="text-3xl font-black text-slate-900">&lt; 1s</p>
              <p className="text-xs font-medium text-slate-500 mt-0.5">QR Ticket Verification</p>
            </div>
            <div>
              <p className="text-3xl font-black text-slate-900">0</p>
              <p className="text-xs font-medium text-slate-500 mt-0.5">Duplicate Check-Ins</p>
            </div>
            <div>
              <p className="text-3xl font-black text-slate-900">99.9%</p>
              <p className="text-xs font-medium text-slate-500 mt-0.5">Uptime & Reliability</p>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Events Preview */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-8 gap-4">
          <div>
            <span className="text-xs font-bold text-violet-600 uppercase tracking-widest">
              Happening Soon
            </span>
            <h2 className="text-2xl sm:text-3xl font-black text-slate-900 mt-1">
              Featured Campus Happenings
            </h2>
          </div>
          <Link
            to="/events"
            className="inline-flex items-center gap-1.5 text-sm font-bold text-violet-600 hover:text-violet-700 transition-colors"
          >
            <span>View Full Schedule</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {featuredEvents.map((event) => (
            <Link
              key={event.id}
              to={`/events/${event.id}`}
              className="group bg-white rounded-3xl border border-slate-200/80 overflow-hidden shadow-sm hover:shadow-xl hover:border-violet-200 transition-all duration-300 flex flex-col"
            >
              <div className="h-48 w-full bg-slate-100 relative overflow-hidden">
                <img
                  src={
                    event.image_url ||
                    'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&auto=format&fit=crop&q=80'
                  }
                  alt={event.title}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <div className="absolute top-3 left-3 px-3 py-1 bg-white/90 backdrop-blur-md rounded-full text-xs font-bold text-slate-800 shadow-sm flex items-center gap-1">
                  <span>{getCategoryIcon(event.category)}</span>
                  <span>{event.category}</span>
                </div>
              </div>

              <div className="p-6 flex-1 flex flex-col justify-between">
                <div>
                  <h3 className="text-lg font-bold text-slate-900 group-hover:text-violet-600 transition-colors line-clamp-1">
                    {event.title}
                  </h3>
                  <p className="mt-2 text-xs text-slate-500 line-clamp-2 leading-relaxed">
                    {event.description}
                  </p>
                </div>

                <div className="mt-6 pt-4 border-t border-slate-100 space-y-2 text-xs text-slate-500">
                  <div className="flex items-center gap-2">
                    <Clock className="w-3.5 h-3.5 text-violet-500" />
                    <span>
                      {formatDate(event.date)} • {formatTime(event.time)}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <MapPin className="w-3.5 h-3.5 text-violet-500" />
                    <span className="truncate">{event.location}</span>
                  </div>

                  <div className="pt-2 flex items-center justify-between">
                    <div className="text-[11px] font-medium text-slate-400">
                      {event.registered_count} / {event.capacity} registered
                    </div>
                    <span className="text-xs font-bold text-violet-600 group-hover:translate-x-1 transition-transform inline-flex items-center gap-1">
                      Register Now →
                    </span>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* Feature Highlights Grid */}
      <section className="bg-slate-900 text-white py-20 rounded-3xl mx-4 sm:mx-8 px-6 sm:px-12 relative overflow-hidden">
        <div className="max-w-7xl mx-auto relative z-10">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <span className="text-xs font-bold text-cyan-400 uppercase tracking-widest">
              Built For Scale
            </span>
            <h2 className="text-3xl sm:text-4xl font-black tracking-tight mt-2">
              Everything Needed for Seamless Events
            </h2>
            <p className="text-sm text-slate-400 mt-3">
              Eliminate paper tickets, chaotic check-in lines, and manual spreadsheets.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-slate-800/60 p-8 rounded-3xl border border-slate-700/60 backdrop-blur-sm">
              <div className="w-12 h-12 rounded-2xl bg-violet-500/20 text-violet-400 flex items-center justify-center mb-6">
                <QrCode className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold mb-2">Instant QR Passes</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Unique encrypted QR tickets generated in milliseconds. Accessible offline or printable for hassle-free physical entry.
              </p>
            </div>

            <div className="bg-slate-800/60 p-8 rounded-3xl border border-slate-700/60 backdrop-blur-sm">
              <div className="w-12 h-12 rounded-2xl bg-indigo-500/20 text-indigo-400 flex items-center justify-center mb-6">
                <Users className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold mb-2">Automated Waitlist</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                When full, students join fair chronological queues. If a registered attendee cancels, the system automatically promotes the next person.
              </p>
            </div>

            <div className="bg-slate-800/60 p-8 rounded-3xl border border-slate-700/60 backdrop-blur-sm">
              <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center mb-6">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold mb-2">Verified Attendance</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Organizers scan tickets with sub-second response times. Automatic detection blocks duplicate check-ins and invalid codes.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
