import { notebooks, Notebook } from '@/lib/notebook-data';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import PythonModelDisplay from './PythonModelDisplay';
// We must explicitly import the component that renders our sequence of computational proofs.
// This component provides a 'Multiway System' view, showing the causal evolution of our Ethernet models.
import EthernetSequenceDisplay from './EthernetSequenceDisplay';
import PythonCSMACDModelDisplay from './PythonCSMACDModelDisplay';
import PythonRTTModelDisplay from './PythonRTTModelDisplay';

// This page serves as the dedicated "wrapper" for each of our live computational models.
// It provides context, embeds the interactive content, and guides the user to
// related explorations, creating a curated journey through our core arguments.

type RelatedNotebooks = {
  readNext: Notebook;
  mightEnjoy: Notebook;
};

// This function implements the circular linking logic for our models.
// The structure is intentional, guiding the user through a specific path of our arguments.
// It ensures that from any point in our logical chain, the next step is clear.
const getRelatedNotebooks = (currentIndex: number): RelatedNotebooks => {
  const total = notebooks.length;
  // We use modulo arithmetic to create a seamless, circular navigation path.
  // This is a more robust, mathematical approach than a fragile, hardcoded switch statement.
  const readNextIndex = (currentIndex + 1) % total;
  const mightEnjoyIndex = (currentIndex + total - 1) % total; // Previous item

  return {
    readNext: notebooks[readNextIndex],
    mightEnjoy: notebooks[mightEnjoyIndex],
  };
};

// By making this component async, we adhere to the new data-fetching model in Next.js.
// The framework can now correctly await the resolution of dynamic route parameters before rendering,
// preventing race conditions. This ensures a predictable, sequential data flow.
export default async function ModelPage({
  params,
}: {
    params: Promise<{ slug: string }>;
}) {
  // unwrap the params promise
  const { slug } = await params;
  const notebookIndex = notebooks.findIndex(n => n.slug === slug);
  const notebook = notebooks[notebookIndex];

  if (!notebook) {
    notFound();
  }

  const { readNext, mightEnjoy } = getRelatedNotebooks(notebookIndex);

  return (
    <div
      className={`bg-white dark:bg-gray-900 py-12 ${notebook.type.startsWith('python') || notebook.type === 'placeholder'
        ? 'text-gray-200 dark:text-gray-200'
        : 'text-gray-800 dark:text-gray-200'
        }`}
    >
      <main id="content" className="content" role="main">
        <article className="post">
          <header className="post-header text-center mb-8">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white">{notebook.title}</h1>
            <time className="post-date mt-2">
              {new Date(notebook.date).toLocaleDateString('en-US', { day: 'numeric', month: 'long', year: 'numeric' })}
            </time>
          </header>

          <section className="post-content">
            <p className="text-lg text-center max-w-3xl mx-auto mb-8">{notebook.description}</p>
            {/* This container uses a CSS trick to break out of the parent's width constraints, achieving a full-width effect.
                It is a visual representation of escaping a constrained model to utilize the full available space. */}
            <div className="wolfram-embed-container my-8">
              <div className="border-y border-gray-200 dark:border-gray-700 shadow-lg bg-gray-50 dark:bg-gray-800">
                {notebook.type === 'wolfram' ? (
                  <iframe
                    key={notebook.url}
                    src={notebook.url}
                    title={notebook.title}
                    className="w-full h-[85vh]"
                    frameBorder="0"
                    allowFullScreen
                  ></iframe>
                ) : notebook.type === 'python' ? (
                  <PythonModelDisplay />
                ) : notebook.type === 'python-csma' ? (
                  <PythonCSMACDModelDisplay />
                ) : notebook.type === 'python-rtt' ? (
                  <PythonRTTModelDisplay />
                      ) : notebook.type === 'python-sequence' ? (
                        <EthernetSequenceDisplay />
                        ) : notebook.type === 'placeholder' ? (
                          // An empty state for models that are not yet built.
                          // This fulfills the requirement for a page that exists but is empty,
                          // serving as a commitment to future work.
                          <div className="flex items-center justify-center h-[85vh] bg-gray-800 text-gray-400">
                            <div className="text-center">
                              <h2 className="text-2xl font-semibold">Model Coming Soon</h2>
                              <p className="mt-2">This computational proof is currently under construction.</p>
                            </div>
                          </div>
                ) : null}
              </div>
            </div>
          </section>
        </article>

        {/* This section ensures that our arguments do not exist in isolation.
            It guides the user to the next logical step in the chain of reasoning,
            reinforcing the connections between our computational proofs. */}
        <section className="read-next">
          <Link href={`/models/${readNext.slug}`} className="read-next-story">
            <div className="post">
              <h2 className="post-title">{readNext.title}</h2>
            </div>
          </Link>
          <Link href={`/models/${mightEnjoy.slug}`} className="read-next-story prev">
            <div className="post">
              <h2 className="post-title">{mightEnjoy.title}</h2>
            </div>
          </Link>
        </section>
      </main>
    </div>
  );
}