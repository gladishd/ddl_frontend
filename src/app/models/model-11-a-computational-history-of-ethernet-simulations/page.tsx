import Link from 'next/link';
import Model11SequenceDisplay from './Model11SequenceDisplay';
import { notebooks, Notebook } from '@/lib/notebook-data';

export const metadata = {
  title: 'Model 11 – A Computational History of Ethernet Simulations',
  description: 'Twenty-five Python simulations of Ethernet contention and related fabrics, with outputs and sequence diagrams.',
};

// helper to pick next & previous in our circular list
function getRelatedNotebooks(currentIndex: number) {
  const total = notebooks.length;
  const readNextIndex = (currentIndex + 1) % total;
  const mightEnjoyIndex = (currentIndex + total - 1) % total;
  return {
    readNext: notebooks[readNextIndex],
    mightEnjoy: notebooks[mightEnjoyIndex],
  };
}

export default function Model11Page() {
  // find ourselves in the global list
  const currentIndex = notebooks.findIndex(
    (n) => n.slug === 'model-11-a-computational-history-of-ethernet-simulations'
  );
  const { readNext, mightEnjoy } = getRelatedNotebooks(currentIndex);

  return (
    <div className="bg-white dark:bg-gray-900 py-12 text-gray-200">
      <main id="content" className="content" role="main">
        <article className="post">
          <header className="post-header text-center mb-8">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white">
              Model 11 – A Computational History of Ethernet Simulations
            </h1>
            <time className="post-date mt-2" dateTime="2025-06-20">
              June 20, 2025
            </time>
          </header>

          <section className="post-content">
            <p className="text-lg text-center max-w-3xl mx-auto mb-8">
              Twenty-five Python simulations of Ethernet contention and related fabrics, with outputs and sequence diagrams.
            </p>

            <div className="wolfram-embed-container my-8">
              <div className="border-y border-gray-200 dark:border-gray-700 shadow-lg bg-gray-50 dark:bg-gray-800">
                <Model11SequenceDisplay />
              </div>
            </div>
          </section>
        </article>

        {/* ← Read Next / You Might Enjoy → */}
        <section className="read-next flex justify-between mt-12">
          <Link
            href={`/models/${mightEnjoy.slug}`}
            className="read-next-story prev flex-1 mr-4 p-6 bg-gray-100 dark:bg-gray-800 rounded-lg hover:shadow-lg transition"
          >
            <span className="block text-sm text-muted-foreground">← You might enjoy</span>
            <h2 className="text-lg font-semibold mt-1">{mightEnjoy.title}</h2>
          </Link>
          <Link
            href={`/models/${readNext.slug}`}
            className="read-next-story flex-1 ml-4 p-6 bg-gray-100 dark:bg-gray-800 rounded-lg hover:shadow-lg transition text-right"
          >
            <span className="block text-sm text-muted-foreground">Read next →</span>
            <h2 className="text-lg font-semibold mt-1">{readNext.title}</h2>
          </Link>
        </section>
      </main>
    </div>
  );
}
