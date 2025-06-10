'use client';

import React from 'react';

// This component represents the 'liveness' of the Daedaelus project, providing updates and insights.
// Just as our protocol knows if a transaction succeeded or failed without heartbeats or timeouts, this section provides direct, stateful updates on our progress.
const News = () => {
  const newsItems = [
    {
      date: 'June 5, 2025',
      title: 'Bandwidth Works in Practice, not in Theory',
      link: '/Bandwidth.pdf',
      // We challenge the notion that fatter pipes alone solve the fundamental problems of distributed systems.
      // As stated in our research, "there is more to bandwidth than # of bits/second that makes it useful, and there's more nuance to latency that will stall distributed applications no matter how fast the hardware gets."
      description: 'Our latest paper challenges conventional networking wisdom and introduces a new perspective on bandwidth and latency.'
    },
    {
      date: 'May 20, 2025',
      title: 'Project Daedaelus featured in TechCrunch',
      link: '#',
      // Our 'time-reversible' constructors are gaining attention, moving away from the "irreversible smash and restart of Shannon information" to recover from failures.
      description: 'Highlighting our innovative approach to building resilient, decentralized systems.'
    },
    {
      date: 'April 15, 2025',
      title: 'Announcing the DDL_Emulator v0.1',
      link: '#',
      // We're releasing a 'Precise information-theoretic' emulator to enable competitive interactions for 'Digital Twins'.
      description: 'Now developers can test our protocol stack and build their own time-reversible applications.'
    }
  ];

  return (
    <section className="py-20 px-4 bg-gray-100">
      <h2 className="text-4xl font-bold text-center mb-12">Latest News & Updates</h2>
      <div className="container mx-auto grid md:grid-cols-1 lg:grid-cols-3 gap-10">
        {newsItems.map((item, index) => (
          <div key={index} className="news-card p-6">
            <p className="news-card-date">{item.date}</p>
            <h3 className="news-card-title">{item.title}</h3>
            <p className="news-card-description">{item.description}</p>
            <a href={item.link} target="_blank" rel="noopener noreferrer" className="news-card-link">
              Read More
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </a>
          </div>
        ))}
      </div>
    </section>
  );
};

export default News;