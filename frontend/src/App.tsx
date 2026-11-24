import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';

// Layouts
import { Layout } from './components/layout/Layout';
import { AdminLayout } from './components/layout/AdminLayout';

// Auth Pages
import { LoginPage } from './pages/auth/LoginPage';
import { RegisterPage } from './pages/auth/RegisterPage';

// Student Pages
import { LandingPage } from './pages/student/LandingPage';
import { EventsPage } from './pages/student/EventsPage';
import { EventDetailPage } from './pages/student/EventDetailPage';
import { DashboardPage } from './pages/student/DashboardPage';
import { MyRegistrationsPage } from './pages/student/MyRegistrationsPage';
import { RegistrationConfirmPage } from './pages/student/RegistrationConfirmPage';
import { QRTicketPage } from './pages/student/QRTicketPage';
import { ProfilePage } from './pages/student/ProfilePage';

// Admin Pages
import { AdminDashboardPage } from './pages/admin/AdminDashboardPage';
import { EventManagementPage } from './pages/admin/EventManagementPage';
import { ParticipantManagementPage } from './pages/admin/ParticipantManagementPage';
import { AttendanceManagementPage } from './pages/admin/AttendanceManagementPage';
import { AnalyticsPage } from './pages/admin/AnalyticsPage';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 text-xs font-semibold text-slate-400">
        Authenticating...
      </div>
    );
  }
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public / Landing */}
          <Route element={<Layout />}>
            <Route path="/" element={<LandingPage />} />
            <Route path="/events" element={<EventsPage />} />
            <Route path="/events/:eventId" element={<EventDetailPage />} />

            {/* Student Protected Routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/my-registrations"
              element={
                <ProtectedRoute>
                  <MyRegistrationsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/registration/confirm/:regId"
              element={
                <ProtectedRoute>
                  <RegistrationConfirmPage />
                </ProtectedRoute>
              }
            />
            <Route path="/ticket/:qrCode" element={<QRTicketPage />} />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <ProfilePage />
                </ProtectedRoute>
              }
            />
          </Route>

          {/* Auth Pages without Main Layout */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Admin Protected Routes */}
          <Route
            path="/admin"
            element={
              <ProtectedRoute>
                <AdminLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<AdminDashboardPage />} />
            <Route path="events" element={<EventManagementPage />} />
            <Route path="participants" element={<ParticipantManagementPage />} />
            <Route path="attendance" element={<AttendanceManagementPage />} />
            <Route path="analytics" element={<AnalyticsPage />} />
          </Route>

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
