import { useEffect, useMemo, useState } from 'react';
import type { Session } from '@supabase/supabase-js';
import { supabase } from '../lib/supabaseClient';
import { clearLastScanResult, restoreLatestScanResult, setScanStorageUser } from '../lib/scanStorage';
import { AuthContext, type AuthState } from './authContext';

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!supabase) {
      setLoading(false);
      return;
    }

    void supabase.auth.getSession().then(async ({ data }) => {
      const userId = data.session?.user.id ?? null;
      setScanStorageUser(userId);
      if (userId) await restoreLatestScanResult(userId);
      setSession(data.session);
      setLoading(false);
    });

    const { data } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      window.setTimeout(() => void (async () => {
        const userId = nextSession?.user.id ?? null;
        setScanStorageUser(userId);
        if (userId) await restoreLatestScanResult(userId);
        setSession(nextSession);
        setLoading(false);
      })(), 0);
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
