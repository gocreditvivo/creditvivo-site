import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from './authContext';
import { isSupabaseConfigured } from '../lib/supabaseClient';

export default function ProtectedRoute() {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (!isSupabaseConfigured) {
    return <Navigate to="/login" replace state={{ from: location.pathname, configurationError: true }} />;
  }

  if (loading) {
    return <div className="min-h-screen bg-navy-950 p-10 text-center text-sm text-white">Opening your secure workspace...</div>;
  }

  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  return <Outlet />;
}
