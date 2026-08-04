import { useEffect, useMemo, useState } from 'react';
import type { Session } from '@supabase/supabase-js';
import { supabase } from '../lib/supabaseClient';
import { clearLastScanResult, setScanStorageUser } from '../lib/scanStorage';
import { AuthContext, type AuthState } from './authContext';

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!supabase) {
      setLoading(false);
      return;
    }

    void supabase.auth.getSession().then(({ data }) => {
      setScanStorageUser(data.session?.user.id ?? null);
      setSession(data.session);
      setLoading(false);
    });

    const { data } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      setScanStorageUser(nextSession?.user.id ?? null);
      setSession(nextSession);
      setLoading(false);
    });

    return () => data.subscription.unsubscribe();
  }, []);

  const value = useMemo<AuthState>(() => ({
    session,
    user: session?.user ?? null,
    loading,
    signOut: async () => {
      clearLastScanResult();
      setScanStorageUser(null);
      if (supabase) await supabase.auth.signOut();
    },
  }), [session, loading]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
