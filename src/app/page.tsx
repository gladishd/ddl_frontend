// src/app/page.tsx
"use client";

import { MacMiniProvider } from "@/context/MacMiniContext";
import DashboardContent from "@/components/DashboardContent";
import LandingPage from "@/components/landing/LandingPage";

export default function DashboardPage() {
  return (
    <MacMiniProvider>
      <LandingPage />
      <DashboardContent />
    </MacMiniProvider>
  );
}