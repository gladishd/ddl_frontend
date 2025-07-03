'use client';
import { pdfjs } from 'react-pdf';

// Put this once – e.g. in src/pdfWorker.ts and import it from _app.tsx
/* one-liner that works in dev + prod ------------------------------- */
pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',   // 👈 switch to .mjs
  import.meta.url,
).toString();