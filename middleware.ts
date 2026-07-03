// Optional route-protection starter.
// Connect this to your real auth provider before live launch.
// This file is intentionally conservative and does not implement fake auth.

import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const requireAuth = process.env.NEXT_PUBLIC_CREDIT_VIVO_REQUIRE_AUTH !== "false";
  const isMemberRoute = request.nextUrl.pathname.startsWith("/member");

  if (!requireAuth || !isMemberRoute) {
    return NextResponse.next();
  }

  // TODO: Replace with real session check from Clerk/Auth0/NextAuth/Supabase Auth.
  // Until real auth is connected, do not expose customer data from backend.
  return NextResponse.next();
}

export const config = {
  matcher: ["/member/:path*"],
};
