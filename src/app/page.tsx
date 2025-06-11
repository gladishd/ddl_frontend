"use client";

import dynamic from "next/dynamic";
import { MacMiniProvider } from "@/context/MacMiniContext";
import DashboardContent from "@/components/DashboardContent";
import WolframNotebookEmbed from "@/components/WolframNotebookEmbed"; // Your updated component

// The landing page is now a pure-client component.
const LandingPage = dynamic(
  () => import("@/components/landing/LandingPage"),
  { ssr: false, loading: () => null }
);

export default function DashboardPage() {
  // Define the list of notebook URLs you want to display
  const notebookUrls = [
    "https://www.wolframcloud.com/obj/gladishdean/Published/wolfram%20cloud%20for%20sahas.nb",
    "https://www.wolframcloud.com/obj/gladishdean/Published/wolfram%20cloud%20for%20sahas2.nb"
  ];

  return (
    <MacMiniProvider>
      <LandingPage />
      <DashboardContent />

      {/* Container for the notebooks */}
      <div className="p-6 bg-gray-50">
        <h2 className="text-3xl font-bold text-center mb-8">Wolfram Notebooks</h2>
        <div className="max-w-4xl mx-auto">
          {notebookUrls.map((url, index) => (
            <WolframNotebookEmbed key={index} notebookUrl={url} />
          ))}
        </div>
      </div>
    </MacMiniProvider>
  );
}