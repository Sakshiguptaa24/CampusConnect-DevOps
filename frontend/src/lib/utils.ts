import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { format, parseISO, isValid } from 'date-fns';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(dateStr: string): string {
  try {
    const date = parseISO(dateStr);
    if (!isValid(date)) return dateStr;
    return format(date, 'MMM dd, yyyy');
  } catch {
    return dateStr;
  }
}

export function formatTime(timeStr: string): string {
  try {
    if (timeStr.includes(':')) {
      const [hours, minutes] = timeStr.split(':').map(Number);
      const period = hours >= 12 ? 'PM' : 'AM';
      const h = hours % 12 || 12;
      return `${h}:${minutes.toString().padStart(2, '0')} ${period}`;
    }
    return timeStr;
  } catch {
    return timeStr;
  }
}

export function getStatusColor(status: string): string {
  switch (status) {
    case 'confirmed':
      return 'bg-emerald-100 text-emerald-700';
    case 'waitlisted':
      return 'bg-warning-100 text-warning-600';
    case 'attended':
      return 'bg-cyan-100 text-cyan-700';
    case 'cancelled':
      return 'bg-danger-100 text-danger-600';
    default:
      return 'bg-navy-100 text-navy-600';
  }
}

export function getCategoryIcon(category: string): string {
  switch (category.toLowerCase()) {
    case 'technology': return '💻';
    case 'cultural': return '🎭';
    case 'sports': return '⚽';
    case 'workshop': return '🔧';
    case 'seminar': return '📚';
    case 'social': return '🎉';
    case 'career': return '💼';
    case 'music': return '🎵';
    default: return '📌';
  }
}

export function getCategoryColor(category: string): string {
  switch (category.toLowerCase()) {
    case 'technology': return 'bg-violet-100 text-violet-700 border-violet-200';
    case 'cultural': return 'bg-pink-100 text-pink-700 border-pink-200';
    case 'sports': return 'bg-emerald-100 text-emerald-700 border-emerald-200';
    case 'workshop': return 'bg-orange-100 text-orange-700 border-orange-200';
    case 'seminar': return 'bg-indigo-100 text-indigo-700 border-indigo-200';
    case 'social': return 'bg-cyan-100 text-cyan-700 border-cyan-200';
    default: return 'bg-navy-100 text-navy-700 border-navy-200';
  }
}
