import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from './authContext';

export default function RoleProtectedRoute({ allowedRoles }: { allowedRoles: string[] }) {
  const { user, loading } = useAuth();
  if (loading) return null;
  const role = String(user?.app_metadata?.role || user?.user_metadata?.role || 'member');
  if (!user || !allowedRoles.includes(role)) return <Navigate to="/dashboard" replace />;
  return <Outlet />;
}
