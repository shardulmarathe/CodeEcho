import { createBrowserClient } from "@supabase/ssr";
import type { SupabaseClient } from "@supabase/supabase-js";

const url = process.env.NEXT_PUBLIC_SUPABASE_URL ?? "";
const anon = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? "";

export const supabaseConfigured = Boolean(url && anon);

let _browser: SupabaseClient | null = null;

/** Browser client. Null when env is missing (guest-only). Cached so AuthBridge
 * and AuthControls share one GoTrue client. */
export function getBrowserClient(): SupabaseClient | null {
  if (!supabaseConfigured) return null;
  if (!_browser) {
    _browser = createBrowserClient(url, anon);
  }
  return _browser;
}
