// src/app/page.tsx
"use client";

import { MacMiniProvider } from "@/context/MacMiniContext";
import DashboardContent from "@/components/DashboardContent";

export default function DashboardPage() {
  return (
    <MacMiniProvider>
      <DashboardContent />
    </MacMiniProvider>
  );
}