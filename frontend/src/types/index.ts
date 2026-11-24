export interface User {
  id: number;
  email: string;
  full_name: string;
  is_admin: boolean;
  is_active: boolean;
  phone?: string;
  department?: string;
  created_at: string;
}

export interface Event {
  id: number;
  title: string;
  description: string;
  date: string;
  time: string;
  end_time?: string;
  location: string;
  category: string;
  capacity: number;
  registered_count: number;
  image_url?: string;
  is_active: boolean;
  created_by: number;
  created_at: string;
  updated_at?: string;
}

export interface Registration {
  id: number;
  user_id: number;
  event_id: number;
  status: 'confirmed' | 'waitlisted' | 'cancelled' | 'attended';
  qr_code: string;
  registered_at: string;
  cancelled_at?: string;
  waitlist_position?: number;
  event?: Event;
  user?: User;
}

export interface EventFilters {
  search?: string;
  category?: string;
  date_from?: string;
  date_to?: string;
  is_active?: boolean;
  page?: number;
  limit?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface DashboardStats {
  total_events: number;
  total_registrations: number;
  attendance_rate: number;
  active_events: number;
  total_users?: number;
  upcoming_events?: number;
}

export interface Analytics {
  registrations_over_time: { date: string; count: number }[];
  category_breakdown: { category: string; count: number }[];
  attendance_stats: { event_title: string; registered: number; attended: number; rate: number }[];
  top_events: { title: string; registrations: number }[];
  capacity_utilization: { title: string; capacity: number; registered: number; utilization: number }[];
}

export interface StudentDashboardStats {
  total_registered: number;
  upcoming_events: number;
  attended: number;
  waitlisted: number;
}
