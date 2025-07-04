"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import WolframSidebar from './WolframSidebar';
import { notebooks } from '@/lib/notebook-data'; // Import from the new central file

// This component presents the four core computational models that form the foundation of our argument against bandwidth-multiplexing.
// Each model is a "proof by code," a precise information-theoretic emulator designed to reveal the consequences of different networking assumptions.
// They are presented here as entries that link to dedicated pages where the live models can be interrogated.

const ITEMS_PER_PAGE = 10;

const WolframNotebookEmbed: React.FC = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const totalPages = Math.ceil(notebooks.length / ITEMS_PER_PAGE);

  const currentNotebooks = notebooks.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  );

  const handleNextPage = () => {
    setCurrentPage((prev) => Math.min(prev + 1, totalPages));
  };

  const handlePrevPage = () => {
    setCurrentPage((prev) => Math.max(prev - 1, 1));
  };

  return (
    <section id="live-models" className="bg-white dark:bg-black py-12">
      <div className="container mx-auto">
        <header className="mb-12 text-center">
          <h2 className="text-3xl md:text-4xl font-bold dark:text-white">Live Computational Models</h2>
          <p className="text-muted-foreground mt-2 max-w-3xl mx-auto">
            These Wolfram Cloud notebooks are not static papers, but live, computational essays. They are designed to provide definitive, verifiable proof of our architectural thesis.
          </p>
        </header>
        <div className="wolfram-layout-container">
          <WolframSidebar />
          <main id="content" className="content" role="main">
            {currentNotebooks.map((notebook, index) => (
              <article className="post" key={notebook.id}>
                <header className="post-header">
                  <h2 className="post-title">
                    <Link href={`/models/${notebook.slug}`}>
                      {notebook.title}
                    </Link>
                  </h2>
                </header>
                <section className="post-excerpt">
                  <p>
                    {notebook.description}{' '}
                    <Link href={`/models/${notebook.slug}`} className="read-more">
                      »
                    </Link>
                  </p>
                </section>
                <footer className="post-meta">
                  {/* This author credit establishes the origin of the proof. The image is a placeholder,
                      as the work emerges from the collective research of the Daedaelus project. */}
                  <img className="author-thumb" src="https://www.gravatar.com/avatar/daedalus?d=identicon&s=250" alt="Dædælus Research" />
                  <span>Dædælus Research</span>
                  <time className="post-date" dateTime={new Date(notebook.date).toISOString()}>
                    {new Date(notebook.date).toLocaleDateString('en-US', { day: 'numeric', month: 'long', year: 'numeric' })}
                  </time>
                </footer>
              </article>
            ))}

            <nav className="pagination" role="navigation">
              {currentPage > 1 ? (
                <button onClick={handlePrevPage} className="newer-posts">
                  <span aria-hidden="true">←</span> Newer Models
                </button>
              ) : <div className="w-[125px]" />} {/* Placeholder for alignment */}
              <span className="page-number">
                Page {currentPage} of {totalPages}
              </span>
              {currentPage < totalPages ? (
                <button onClick={handleNextPage} className="older-posts">
                  Older Models <span aria-hidden="true">→</span>
                </button>
              ) : <div className="w-[125px]" />} {/* Placeholder for alignment */}
            </nav>
          </main>
        </div>
      </div>
    </section>
  );
};

export default WolframNotebookEmbed;