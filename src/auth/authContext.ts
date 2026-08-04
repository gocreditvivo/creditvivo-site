import { createContext, useContext } from 'react';
import type { Session, User } from '@supabase/supabase-js';

export type AuthState = {
  session: Session | null;
  user: User | null;
  loading: boolean;
  signOut: () => Promise<void>;
};

export const AuthContext = createContext<AuthState>({ session: null, user: null, loading: true, signOut: async () => undefined });

export function useAuth() {
  return useContext(AuthContext);
}
