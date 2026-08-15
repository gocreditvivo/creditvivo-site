import { supabase } from './supabaseClient';

export async function authenticatedFetch(input: RequestInfo | URL, init: RequestInit = {}) {
  if (!supabase) throw new Error('Secure sign-in is not configured.');
  const { data, error } = await supabase.auth.getSession();
  if (error || !data.session?.access_token) throw new Error('Please sign in again.');
  const headers = new Headers(init.headers);
  headers.set('Authorization', `Bearer ${data.session.access_token}`);
  return fetch(input, { ...init, headers });
}
