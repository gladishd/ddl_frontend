import React, { ReactNode } from 'react'
import Head from 'next/head'
import Link from 'next/link'

interface SimulationLayoutProps {
  title: string
  description: string
  scriptsFolder: string
  children: ReactNode
}

const SimulationLayout: React.FC<SimulationLayoutProps> = ({
  title,
  description,
  scriptsFolder,
  children,
}) => {
  return (
    <>
      <Head>
        <title>{title}</title>
        <meta name="description" content={description} />
      </Head>

      <div className="container mx-auto py-8 px-4">
        <header className="mb-8">
          <h1 className="text-3xl font-bold">{title}</h1>
          <p className="text-lg text-muted-foreground mt-2">{description}</p>
          <Link
            href={scriptsFolder}
            className="text-sm text-blue-500 hover:underline"
            target="_blank"
          >
            Browse Python scripts
          </Link>
        </header>

        <main>{children}</main>
      </div>
    </>
  )
}

export default SimulationLayout
