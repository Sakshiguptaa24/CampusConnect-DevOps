import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useEvents } from '@/hooks/useEvents';
import { SearchBar } from '@/components/shared/SearchBar';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { EmptyState } from '@/components/shared/EmptyState';
import { Badge } from '@/components/shared/Badge';
import { Calendar, Clock, MapPin, Users, ArrowRight } from 'lucide-react';
import { formatDate, formatTime, getCategoryIcon } from '@/lib/utils';

export const EventsPage: React.FC = () => {
  const categories = [
    { label: 'All Events', value: 'all' },
    { label: 'Technology', value: 'Technology' },
    { label: 'Cultural', value: 'Cultural' },
    { label: 'Sports', value: 'Sports' },
    { label: 'Workshop', value: 'Workshop' },
    { label: 'Seminar', value: 'Seminar' },
  ];

  const [activeCategory, setActiveCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  const { events, total, pages, isLoading, filters, updateFilters } = useEvents({
    page: 1,
    limit: 9,
  });

  const handleCategoryChange = (cat: string) => {
    setActiveCategory(cat);
    updateFilters({ category: cat === 'all' ? undefined : cat, page: 1 });
  };

  const handleSearchChange = (term: string) => {
    setSearchTerm(term);
    updateFilters({ search: term || undefined, page: 1 });
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8 animate-fadeIn">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Discover Events</h1>
          <p className="text-sm text-slate-500 mt-1">
            Browse and register for upcoming college conferences, workshops, and festivals
          </p>
        </div>
        <div className="text-xs font-semibold text-slate-500 bg-white border border-slate-200 px-3 py-1.5 rounded-xl shadow-sm self-start md:self-auto">
          {total} Active Events Found
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="space-y-4">
        <SearchBar
          value={searchTerm}
          onChange={handleSearchChange}
          placeholder="Search by title, department, or keyword..."
        />

        {/* Category Filter Pills */}
        <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
          {categories.map((cat) => {
            const active = activeCategory === cat.value;
            return (
              <button
                key={cat.value}
                onClick={() => handleCategoryChange(cat.value)}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all whitespace-nowrap ${
                  active
                    ? 'bg-violet-600 text-white shadow-md shadow-violet-200'
                    : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200/80'
                }`}
              >
                {cat.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Content */}
      {isLoading ? (
        <LoadingSpinner text="Loading campus events..." className="py-20" />
      ) : events.length === 0 ? (
        <EmptyState
          title="No events found"
          description="Try broadening your search term or selecting another category filter."
          actionLabel="Clear Filters"
          onAction={() => {
            setActiveCategory('all');
            setSearchTerm('');
            updateFilters({ search: undefined, category: undefined, page: 1 });
          }}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {events.map((event) => {
            const isFull = event.registered_count >= event.capacity;
            const fillPercent = Math.min(
              100,
              Math.round((event.registered_count / event.capacity) * 100)
            );

            return (
              <div
                key={event.id}
                className="bg-white rounded-3xl border border-slate-200/80 overflow-hidden shadow-sm hover:shadow-xl hover:border-violet-300 transition-all duration-300 flex flex-col justify-between group"
              >
                {/* Event Image */}
                <div className="h-48 w-full bg-slate-100 relative overflow-hidden">
                  <img
                    src={
                      event.image_url ||
                      'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&auto=format&fit=crop&q=80'
                    }
                    alt={event.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute top-3 left-3 flex items-center gap-1.5">
                    <span className="px-3 py-1 bg-white/95 backdrop-blur-md rounded-full text-xs font-bold text-slate-800 shadow-sm flex items-center gap-1">
                      <span>{getCategoryIcon(event.category)}</span>
                      <span>{event.category}</span>
                    </span>
                  </div>
                  <div className="absolute top-3 right-3">
                    {isFull ? (
                      <span className="px-2.5 py-1 bg-amber-500 text-white rounded-full text-[11px] font-bold shadow-sm">
                        Waitlist Active
                      </span>
                    ) : (
                      <span className="px-2.5 py-1 bg-emerald-500 text-white rounded-full text-[11px] font-bold shadow-sm">
                        Seats Available
                      </span>
                    )}
                  </div>
                </div>

                {/* Event Details */}
                <div className="p-6 flex-1 flex flex-col justify-between">
                  <div>
                    <h3 className="text-lg font-bold text-slate-900 group-hover:text-violet-600 transition-colors line-clamp-1">
                      {event.title}
                    </h3>
                    <p className="mt-2 text-xs text-slate-500 line-clamp-2 leading-relaxed">
                      {event.description}
                    </p>

                    <div className="mt-4 space-y-2 text-xs text-slate-600">
                      <div className="flex items-center gap-2">
                        <Calendar className="w-3.5 h-3.5 text-violet-500 flex-shrink-0" />
                        <span>{formatDate(event.date)}</span>
                        <span className="text-slate-300">•</span>
                        <Clock className="w-3.5 h-3.5 text-violet-500 flex-shrink-0" />
                        <span>{formatTime(event.time)}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <MapPin className="w-3.5 h-3.5 text-violet-500 flex-shrink-0" />
                        <span className="truncate">{event.location}</span>
                      </div>
                    </div>
                  </div>

                  {/* Capacity Bar & Action */}
                  <div className="mt-6 pt-4 border-t border-slate-100">
                    <div className="flex items-center justify-between text-xs mb-1.5">
                      <span className="text-slate-500 flex items-center gap-1">
                        <Users className="w-3.5 h-3.5" /> Capacity
                      </span>
                      <span className="font-bold text-slate-700">
                        {event.registered_count} / {event.capacity}
                      </span>
                    </div>
                    {/* Progress Bar */}
                    <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden mb-4">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          fillPercent >= 100
                            ? 'bg-amber-500'
                            : fillPercent >= 80
                            ? 'bg-indigo-500'
                            : 'bg-emerald-500'
                        }`}
                        style={{ width: `${fillPercent}%` }}
                      />
                    </div>

                    <Link
                      to={`/events/${event.id}`}
                      className="w-full py-2.5 px-4 rounded-xl bg-slate-900 hover:bg-violet-600 text-white font-bold text-xs flex items-center justify-center gap-1.5 transition-colors shadow-sm"
                    >
                      <span>{isFull ? 'View / Join Waitlist' : 'View & Register'}</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Pagination Controls */}
      {pages > 1 && (
        <div className="flex items-center justify-center gap-2 pt-6">
          <button
            onClick={() => updateFilters({ page: (filters.page || 1) - 1 })}
            disabled={(filters.page || 1) <= 1}
            className="px-4 py-2 rounded-xl text-xs font-semibold bg-white border border-slate-200 text-slate-700 disabled:opacity-40 hover:bg-slate-50"
          >
            Previous
          </button>
          <span className="text-xs text-slate-500 font-medium px-2">
            Page {filters.page || 1} of {pages}
          </span>
          <button
            onClick={() => updateFilters({ page: (filters.page || 1) + 1 })}
            disabled={(filters.page || 1) >= pages}
            className="px-4 py-2 rounded-xl text-xs font-semibold bg-white border border-slate-200 text-slate-700 disabled:opacity-40 hover:bg-slate-50"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};
