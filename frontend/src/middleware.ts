import { clerkMiddleware } from "@clerk/nextjs/server";

const clerkEnabled = !!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;

// Clerk middleware only when configured; otherwise a pass-through so the app
// runs in guest-only mode without Clerk keys.
export default clerkEnabled ? clerkMiddleware() : function middleware() {};

export const config = {
  matcher: [
    // Skip Next internals and static files
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    "/(api|trpc)(.*)",
  ],
};
