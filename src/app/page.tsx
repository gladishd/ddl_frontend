// src/app/page.tsx
"use client";

import dynamic from "next/dynamic";
import { MacMiniProvider } from "@/context/MacMiniContext";
import DashboardContent from "@/components/DashboardContent";

// ────────────────────────────────────────────────────────────────
// The landing page is now a pure-client component.
// It never gets server-rendered, so browser extensions that
// mutate inline styles (e.g. Dark Reader) can’t cause a mismatch.
// ────────────────────────────────────────────────────────────────
const LandingPage = dynamic(
  () => import("@/components/landing/LandingPage"),
  { ssr: false, loading: () => null } // no flash-of-empty-div
);

export default function DashboardPage() {
  return (
    <MacMiniProvider>
      <LandingPage />
      <DashboardContent />
    </MacMiniProvider>
  );
}
