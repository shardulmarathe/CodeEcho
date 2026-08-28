import { NextRequest, NextResponse } from "next/server";
import {
  createSupabaseRouteClient,
  safeNextPath,
  supabaseServerConfigured,
} from "@/lib/supabase-server";

function signInErrorRedirect(origin: string, reason: string) {
  const url = new URL("/sign-in", origin);
  url.searchParams.set("error", reason);
  return NextResponse.redirect(url);
}

export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url);
  const code = requestUrl.searchParams.get("code");
  const next = safeNextPath(requestUrl.searchParams.get("next"));
  const origin = requestUrl.origin;
  const otpError =
    requestUrl.searchParams.get("error_code") ||
    requestUrl.searchParams.get("error");

  if (!supabaseServerConfigured) {
    return signInErrorRedirect(origin, "config");
  }
  if (!code) {
    return signInErrorRedirect(origin, otpError === "otp_expired" ? "otp_expired" : "missing_code");
  }

  const redirect = NextResponse.redirect(new URL(next, origin));
  const supabase = createSupabaseRouteClient(request, redirect);
  const { error } = await supabase.auth.exchangeCodeForSession(code);
  if (error) {
    const expired = /expired|invalid/i.test(error.message);
    return signInErrorRedirect(origin, expired ? "otp_expired" : "exchange_failed");
  }
  return redirect;
}
