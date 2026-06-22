import { createClient } from '@supabase/supabase-js'

const url = import.meta.env.VITE_SUPABASE_URL
const anonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!url || !anonKey) {
  // Aviso util em dev: o login nao funciona sem a anon key.
  console.warn('VITE_SUPABASE_URL / VITE_SUPABASE_ANON_KEY ausentes — preencha o .env do Front.')
}

export const supabase = createClient(url, anonKey, {
  auth: { persistSession: true, autoRefreshToken: true },
})
