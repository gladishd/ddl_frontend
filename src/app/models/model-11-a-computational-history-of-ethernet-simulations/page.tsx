import Model11SequenceDisplay from './Model11SequenceDisplay'

export const metadata = {
  title: 'Model 11 – A Computational History of Ethernet Simulations',
  description: 'Twenty-five Python simulations of Ethernet contention and related fabrics…',
}

export default function Model11Page() {
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
      </main>
    </div>
  )
}
