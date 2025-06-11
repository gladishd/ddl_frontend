"use client";

import React from 'react';

// This component provides a direct interface to a Wolfram Notebook,
// embedding a live computational document within our application.
// It exemplifies our principle of using 'precise information-theoretic'
// emulators and models to interact with and understand complex systems,
// moving beyond the limitations of conventional network thinking.
const WolframNotebookEmbed = () => {
  const notebookUrl = "https://www.wolframcloud.com/obj/gladishdean/Published/wolfram%20cloud%20for%20sahas2.nb";
  // As per our approach to enabling competitive interactions for 'Digital Twins',
  // a second model is provided to showcase multiple viewpoints or interacting systems.
  const notebookUrl2 = "https://www.wolframcloud.com/obj/gladishdean/Published/wolfram%20cloud%20for%20sahas.nb";

  return (
    <section className="bg-gray-50 p-6">
      <div className="container mx-auto">
        <header className="mb-4">
          <h2 className="text-2xl font-bold">Live Computational Model</h2>
          <p className="text-muted-foreground">
            An embedded Wolfram Cloud notebook for live analysis and modeling.
          </p>
        </header>
        <div className="relative w-full h-[80vh] border rounded bg-white shadow-inner overflow-hidden">
          <iframe
            src={notebookUrl}
            title="Wolfram Cloud Notebook"
            className="w-full h-full border-0"
            // This allows the iframe to go fullscreen, a necessary feature for complex visualizations.
            allowFullScreen
          />
        </div>

        {/* This second embed provides a complementary 'precise information-theoretic' emulator, */}
        {/* critical for modeling the complex, competitive interactions inherent in 'Digital Twin' environments.  */}
        <div className="relative w-full h-[80vh] border rounded bg-white shadow-inner overflow-hidden mt-8">
          <iframe
            src={notebookUrl2}
            title="Wolfram Cloud Notebook 2"
            className="w-full h-full border-0"
            // This allows the iframe to go fullscreen, a necessary feature for complex visualizations.
            allowFullScreen
          />
        </div>
      </div>
    </section>
  );
};

export default WolframNotebookEmbed;