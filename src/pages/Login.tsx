import { useState } from 'react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import { Lock, ShieldCheck } from 'lucide-react';
import { useAuth } from '../auth/authContext';
import { isSupabaseConfigured, supabase } from '../lib/supabaseClient';

type LocationState = { from?: string; configurationError?: boolean };

export default function Login() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const state = (location.state ?? {}) as LocationState;
  const [mode, setMode] = useState<'login' | 'signup'>('signup');
  const [firstName, setFirstName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);

  if (user) return <Navigate to={state.from || '/dashboard'} replace />;

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage('');
    if (!supabase) {
      setMessage('Customer login is not configured on this deployment yet.');
      return;
    }

    setBusy(true);
    try {
      if (mode === 'signup') {
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
          options: {
            data: { first_name: firstName },
            emailRedirectTo: `${window.location.origin}/login`,
          },
        });
        if (error) throw error;
        if (data.user && data.session) {
          const { error: profileError } = await supabase.from('creditvivo_profiles').upsert({
            id: data.user.id,
            email,
            first_name: firstName,
            updated_at: new Date().toISOString(),
          });
          if (profileError) throw profileError;
          navigate(state.from || '/dashboard', { replace: true });
        } else {
          setMessage('Check your email to confirm your account, then return here to sign in.');
          setMode('login');
        }
      } else {
        const { error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
        navigate(state.from || '/dashboard', { replace: true });
      }
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'We could not open your account.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="min-h-[75vh] bg-gradient-to-b from-sky-50/70 to-white py-14">
      <div className="mx-auto max-w-md px-4">
        <div className="rounded-2xl border border-navy-100 bg-white p-6 shadow-xl shadow-navy-900/5">
          <div className="mb-5 flex h-11 w-11 items-center justify-center rounded-xl bg-navy-950 text-teal-300"><Lock size={20} /></div>
          <p className="text-[11px] font-bold uppercase tracking-widest text-sky-600">Customer test access</p>
          <h1 className="mt-2 text-2xl font-extrabold text-navy-950">{mode === 'signup' ? 'Create your Credit Vivo account' : 'Welcome back'}</h1>
          <p className="mt-2 text-sm leading-6 text-navy-500">Sign in to test the member dashboard and save synthetic demo findings to your private account.</p>

          {state.configurationError && <p className="mt-4 rounded-lg bg-amber-50 p-3 text-xs text-amber-800">This deployment still needs its Supabase environment settings.</p>}

          <form onSubmit={submit} className="mt-6 space-y-4">
            {mode === 'signup' && <label className="block text-xs font-semibold text-navy-700">First name<input required value={firstName} onChange={(event) => setFirstName(event.target.value)} className="mt-1.5 w-full rounded-lg border border-navy-200 px-3 py-2.5 text-sm" /></label>}
            <label className="block text-xs font-semibold text-navy-700">Email<input required type="email" value={email} onChange={(event) => setEmail(event.target.value)} className="mt-1.5 w-full rounded-lg border border-navy-200 px-3 py-2.5 text-sm" /></label>
            <label className="block text-xs font-semibold text-navy-700">Password<input required minLength={8} type="password" value={password} onChange={(event) => setPassword(event.target.value)} className="mt-1.5 w-full rounded-lg border border-navy-200 px-3 py-2.5 text-sm" /></label>
            {message && <p className="rounded-lg bg-sky-50 p-3 text-xs leading-5 text-sky-800">{message}</p>}
            <button disabled={busy} className="btn-primary w-full justify-center py-3 disabled:opacity-60">{busy ? 'Please wait...' : mode === 'signup' ? 'Create test account' : 'Sign in'}</button>
          </form>

          <button type="button" onClick={() => { setMode(mode === 'signup' ? 'login' : 'signup'); setMessage(''); }} className="mt-4 w-full text-xs font-semibold text-sky-700">
            {mode === 'signup' ? 'Already registered? Sign in' : 'Need an account? Create one'}
          </button>

          <div className="mt-6 flex gap-2 rounded-lg bg-navy-50 p-3 text-[11px] leading-5 text-navy-500"><ShieldCheck size={15} className="mt-0.5 shrink-0 text-mint-600" />The public test uses fictional findings. Do not upload a real credit report during this test.</div>
          {!isSupabaseConfigured && <p className="mt-3 text-[11px] font-semibold text-rose-600">Supabase is not configured in this build.</p>}
        </div>
      </div>
    </section>
  );
}
