import { notebooks, Notebook } from '@/lib/notebook-data';
import Link from 'next/link';
import { notFound } from 'next/navigation';

// This page serves as the dedicated "wrapper" for each of our live computational models.
// It provides context, embeds the interactive Wolfram Notebook, and guides the user to
// related explorations, creating a curated journey through our core arguments.

type RelatedNotebooks = {
  readNext: Notebook;
  mightEnjoy: Notebook;
};

// This function implements the circular linking logic for our models.
// The structure is intentional, guiding the user through a specific path of our arguments.
// For instance, from the critique of half-duplex contention (Model 1), we point to our
// ultimate solution (Model 4) and the subsequent problem of full-duplex degradation (Model 2).
const getRelatedNotebooks = (currentIndex: number): RelatedNotebooks => {
  const total = notebooks.length;
  switch (currentIndex) {
    case 0: // Model 1
      return { readNext: notebooks[3], mightEnjoy: notebooks[1] }; // 4, 2
    case 1: // Model 2
      return { readNext: notebooks[0], mightEnjoy: notebooks[2] }; // 1, 3
    case 2: // Model 3
      return { readNext: notebooks[1], mightEnjoy: notebooks[3] }; // 2, 4
    case 3: // Model 4
      return { readNext: notebooks[2], mightEnjoy: notebooks[0] }; // 3, 1
    default:
      // Fallback just in case, though it should not be reached with valid data.
      return { readNext: notebooks[0], mightEnjoy: notebooks[1] };
  }
};

// By making this component async, we adhere to the new data-fetching model in Next.js 15.
// The framework can now correctly await the resolution of dynamic route parameters before rendering,
// preventing the race condition that caused the error. This ensures a predictable, sequential data flow.
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
    <div className="bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-200 py-12">
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
                <iframe
                  key={notebook.url}
                  src={notebook.url}
                  title={notebook.title}
                  className="w-full h-[85vh]"
                  frameBorder="0"
                  allowFullScreen
                ></iframe>
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