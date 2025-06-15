"use client";

import React, { useEffect, useState, useMemo } from "react";
import dynamic from "next/dynamic";

import { MacMiniProvider } from "@/context/MacMiniContext";
import DocumentCard from "@/components/DocumentCard";
import DocumentToc from "@/components/DocumentToc"; // Import new component
import { DocumentRecord } from "@/types/Document";
import { Button } from "@/components/ui/button"; // Import Button
import { Search, List, LayoutGrid } from "lucide-react"; // Import icons

import DashboardContent from "@/components/DashboardContent";
import WolframNotebookEmbed from "@/components/WolframNotebookEmbed";
import "./globals.css";

const LandingPage = dynamic(
  () => import("@/components/landing/LandingPage"),
  { ssr: false, loading: () => null },
);

export default function DashboardPage() {
  const [docs, setDocs] = useState<DocumentRecord[]>([]);
  const [viewMode, setViewMode] = useState<'cards' | 'toc'>('cards');
  const [nameQuery, setNameQuery] = useState('');
  const [tagQuery, setTagQuery] = useState('');

  useEffect(() => {
    fetch("/api/documents")
      .then(r => r.json())
      .then(setDocs)
      .catch(console.error);
  }, []);

  // The GVM must allow for dynamic filtering and re-structuring of its contents.
  // This filtering logic acts as a 'ruleset' to create different Local Observer Views of the library.
  const filteredDocs = useMemo(() => {
    let tempDocs = [...docs];
    if (nameQuery) {
      tempDocs = tempDocs.filter(doc =>
        doc.title.toLowerCase().includes(nameQuery.toLowerCase()) ||
        doc.description?.toLowerCase().includes(nameQuery.toLowerCase())
      );
    }
    if (tagQuery) {
      tempDocs = tempDocs.filter(doc =>
        doc.tags.some(tag => tag.toLowerCase().includes(tagQuery.toLowerCase()))
      );
    }
    return tempDocs;
  }, [docs, nameQuery, tagQuery]);

  return (
    <MacMiniProvider>
      <main className="px-6 py-8">
        <h1 className="text-4xl font-extrabold mb-4">📚 Dædælus Library</h1>

        <div className="flex flex-wrap items-center gap-4 mb-8">
          {/* Search by Name */}
          <div className="relative flex-grow md:flex-grow-0">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search by name..."
              value={nameQuery}
              onChange={(e) => setNameQuery(e.target.value)}
              className="pl-10 w-full md:w-64"
            />
          </div>

          {/* Search by Tags */}
          <div className="relative flex-grow md:flex-grow-0">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search by tags..."
              value={tagQuery}
              onChange={(e) => setTagQuery(e.target.value)}
              className="pl-10 w-full md:w-64"
            />
          </div>

          {/* View Mode Toggle */}
          <div className="flex items-center gap-2 ml-auto">
            <Button variant={viewMode === 'cards' ? 'default' : 'outline'} size="icon" onClick={() => setViewMode('cards')}>
              <LayoutGrid className="h-4 w-4" />
            </Button>
            <Button variant={viewMode === 'toc' ? 'default' : 'outline'} size="icon" onClick={() => setViewMode('toc')}>
              <List className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {viewMode === 'cards' ? (
          <div className="graph-library-masonry-layout">
            {filteredDocs.map(d => (
              <DocumentCard key={d.id} doc={d} />
            ))}
          </div>
        ) : (
          <DocumentToc documents={filteredDocs} />
        )}

        {filteredDocs.length === 0 && !nameQuery && !tagQuery && (
          <p className="text-muted-foreground text-center py-10">No documents available.</p>
        )}
        {filteredDocs.length === 0 && (nameQuery || tagQuery) && (
          <p className="text-muted-foreground text-center py-10">No documents match your search criteria.</p>
        )}
      </main>

      <LandingPage />
      <DashboardContent />
      <WolframNotebookEmbed />
    </MacMiniProvider>
  );
}