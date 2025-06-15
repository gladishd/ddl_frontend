"use client";

import React, { useEffect, useState } from "react";
import dynamic from "next/dynamic";

import { MacMiniProvider } from "@/context/MacMiniContext";
import DocumentCard from "@/components/DocumentCard";
import { DocumentRecord } from "@/types/Document";

import DashboardContent from "@/components/DashboardContent";
import WolframNotebookEmbed from "@/components/WolframNotebookEmbed";
import "./globals.css";

/* marketing splash still lives in LandingPage */
const LandingPage = dynamic(
  () => import("@/components/landing/LandingPage"),
  { ssr: false, loading: () => null },
);

export default function DashboardPage() {
  const [docs, setDocs] = useState<DocumentRecord[]>([]);

  useEffect(() => {
    fetch("/api/documents")
      .then(r => r.json())
      .then(setDocs)
      .catch(console.error);
  }, []);

  return (
    <MacMiniProvider>
      {/* ===== Library ===== */}
      <main className="px-6 py-8">
        <h1 className="text-4xl font-extrabold mb-8">📚 Dædælus Library</h1>

        <div className="graph-library-masonry-layout">
          {docs.map(d => (
            <DocumentCard key={d.id} doc={d} />
          ))}
        </div>
      </main>

      {/* ===== marketing / hero below the fold ===== */}
      <LandingPage />
      <DashboardContent />
      <WolframNotebookEmbed />
    </MacMiniProvider>
  );
}
