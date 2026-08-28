import type { Metadata } from "next";
import { Geist, Space_Grotesk, JetBrains_Mono, Kalam, Patrick_Hand } from "next/font/google";
import { Analytics } from "@vercel/analytics/next";
import { AuthBridge } from "@/components/auth/AuthControls";
import "./globals.css";

const geistSans = Geist({ variable: "--font-sans", subsets: ["latin"] });
const display = Space_Grotesk({
  variable: "--font-display",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});
const mono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});
// Hand-drawn display fonts, headings/wordmark (Kalam) and doodle captions (Patrick Hand).
// Never used for long body text (see globals.css).
const hand = Kalam({
  variable: "--font-hand",
  subsets: ["latin"],
  weight: ["400", "700"],
});
const handBody = Patrick_Hand({
  variable: "--font-hand-body",
  subsets: ["latin"],
  weight: ["400"],
});

const authEnabled = !!(
  process.env.NEXT_PUBLIC_SUPABASE_URL && process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
);

// Canonical site URL: explicit override → Vercel's production URL → localhost.
const siteUrl = process.env.NEXT_PUBLIC_SITE_URL
  ? process.env.NEXT_PUBLIC_SITE_URL.replace(/\/$/, "")
  : process.env.VERCEL_PROJECT_PRODUCTION_URL
    ? `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}`
    : "http://localhost:3000";

const description =
  "Practice answering software-engineering interview questions out loud. Get scored on your reasoning and your delivery.";

// Platforms cache og:image per-URL; versioning with the deploy SHA makes new
// shares fetch the latest screenshot instead of a stale cached one.
const ogImage = `/og-home.png?v=${(process.env.VERCEL_GIT_COMMIT_SHA ?? "dev").slice(0, 8)}`;

// og:image is a screenshot of the homepage, regenerated after every push by
// .github/workflows/og-refresh.yml -> public/og-home.png (committed by CI;
// headless Chrome can't run in Vercel's build container).
export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: "CodeEcho — practice explaining, get the offer",
  description,
  openGraph: {
    title: "CodeEcho — practice explaining, get the offer",
    description,
    url: siteUrl,
    siteName: "CodeEcho",
    type: "website",
    locale: "en_US",
    images: [{ url: ogImage, width: 1200, height: 630, alt: "CodeEcho" }],
  },
  twitter: {
    card: "summary_large_image",
    title: "CodeEcho — practice explaining, get the offer",
    description,
    images: [ogImage],
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  const tree = (
    <html
      lang="en"
      className={`${geistSans.variable} ${display.variable} ${mono.variable} ${hand.variable} ${handBody.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <body className="min-h-full flex flex-col" suppressHydrationWarning>
        {children}
        {authEnabled && <AuthBridge />}
        <Analytics />
      </body>
    </html>
  );

  return tree;
}
