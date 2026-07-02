import type { Metadata } from "next";
import { Geist, Space_Grotesk, JetBrains_Mono, Kalam, Patrick_Hand } from "next/font/google";
import { ClerkProvider } from "@clerk/nextjs";
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
// Hand-drawn display fonts — headings/wordmark (Kalam) and doodle captions (Patrick Hand).
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

const clerkEnabled = !!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;

export const metadata: Metadata = {
  title: "CodeEcho — practice explaining, get the offer",
  description:
    "Practice answering software-engineering interview questions out loud. Get scored on your reasoning and your delivery.",
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
        {clerkEnabled && <AuthBridge />}
      </body>
    </html>
  );

  return clerkEnabled ? <ClerkProvider>{tree}</ClerkProvider> : tree;
}
