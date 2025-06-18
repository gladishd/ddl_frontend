import Link from 'next/link';
import WolframSidebar from '@/components/WolframSidebar';
import { notebooks } from '@/lib/notebook-data';

// This page serves as the central hub for our live computational models.
// By making this a Server Component, we handle pagination via URL search parameters,
// creating a bookmarkable and shareable state for the model list. This is a more
// robust and less fragile architecture than relying on client-side state.
export default async function ModelsPage({
  searchParams,
}: {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
  // unwrap the params promise
  const sp = await searchParams;
  const page = Number(sp.page ?? 1);
  const ITEMS_PER_PAGE = 2;
  const totalPages = Math.ceil(notebooks.length / ITEMS_PER_PAGE);

  const currentNotebooks = notebooks.slice(
    (page - 1) * ITEMS_PER_PAGE,
    page * ITEMS_PER_PAGE
  );

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
            {currentNotebooks.map((notebook) => (
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
                  <img className="author-thumb" src="https://www.gravatar.com/avatar/daedalus?d=identicon&s=250" alt="Dædælus Research" />
                  <span>Dædælus Research</span>
                  <time className="post-date" dateTime={new Date(notebook.date).toISOString()}>
                    {new Date(notebook.date).toLocaleDateString('en-US', { day: 'numeric', month: 'long', year: 'numeric' })}
                  </time>
                </footer>
              </article>
            ))}
            <nav className="pagination" role="navigation">
              {page > 1 ? (
                <Link href={`/models?page=${page - 1}`} className="newer-posts" scroll={false}>
                  <span aria-hidden="true">←</span> Newer Models
                </Link>
              ) : <div className="w-[125px]" />}
              <span className="page-number">
                Page {page} of {totalPages}
              </span>
              {page < totalPages ? (
                <Link href={`/models?page=${page + 1}`} className="older-posts" scroll={false}>
                  Older Models <span aria-hidden="true">→</span>
                </Link>
              ) : <div className="w-[125px]" />}
            </nav>
          </main>
        </div>
      </div>
    </section>
  );
};