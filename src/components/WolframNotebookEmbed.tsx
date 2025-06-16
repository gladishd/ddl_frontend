"use client";

import React from 'react';
import WolframSidebar from './WolframSidebar'; // your existing sidebar

// List the four notebooks in the order you want them rendered:
const notebookUrls = [
  "https://www.wolframcloud.com/obj/gladishdean/Published/wolfram%20cloud%20for%20sahas.nb",
  "https://www.wolframcloud.com/obj/gladishdean/Published/wolfram%20cloud%20for%20sahas2.nb",
  "https://www.wolframcloud.com/obj/gladishdean/Published/wolfram%20cloud%20for%20sahas3.nb",
  "https://www.wolframcloud.com/obj/gladishdean/Published/wolfram%20cloud%20for%20sahas4.nb",
];

const WolframNotebookEmbed: React.FC = () => {
  return (
    <section className="bg-gray-50 p-6">
      <div className="container mx-auto">
        <header className="mb-4">
          <h2 className="text-2xl font-bold">Live Computational Models</h2>
          <p className="text-muted-foreground">
            Embedded Wolfram Cloud notebooks for live analysis and modeling.
          </p>
        </header>
        <div className="wolfram-layout-container">
          <WolframSidebar />

          {/* Stack each notebook iframe with some vertical spacing */}
          <div className="flex flex-col space-y-8 w-full">
            {notebookUrls.map((url) => (
              <div
                key={url}
                className="relative w-full h-[80vh] border rounded bg-white shadow-inner overflow-hidden"
              >
                <iframe
                  src={url}
                  title={`Wolfram Cloud Notebook: ${url.split('/').pop()}`}
                  className="w-full h-full border-0"
                  allowFullScreen
                />
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default WolframNotebookEmbed;
