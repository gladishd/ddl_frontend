'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Heart, Eye, Tag, Share2, ImageOff } from 'lucide-react';
import { pdfjs } from 'react-pdf';
import type { DocumentRecord } from '@/types/Document';
import { Button } from '@/components/ui/button';

/* ------------------------------------------------------------------ */
/*  Configure pdf.js – point the worker to the CDN                    */
/* ------------------------------------------------------------------ */
if (typeof window !== 'undefined' && !pdfjs.GlobalWorkerOptions.workerSrc) {
  /* one-liner that works in dev + prod ------------------------------- */
  pdfjs.GlobalWorkerOptions.workerSrc = new URL(
    'pdfjs-dist/build/pdf.worker.min.mjs',   // 👈 switch to .mjs
    import.meta.url,
  ).toString();
}

type Props = { doc: DocumentRecord };

export default function DocumentCard({ doc }: Props) {
  /* -------------------------------------------------------------- */
  /*  State                                                         */
  /* -------------------------------------------------------------- */
  const [likes, setLikes] = useState<number>(doc.likes);
  const [views, setViews] = useState<number>(doc.views);
  const [tagsOpen, setTagsOpen] = useState<boolean>(false);
  const [tagDraft, setTagDraft] = useState<string>(doc.tags.join(', '));

  // thumbnail
  const [thumbUrl, setThumbUrl] = useState<string | null>(null); // null = loading, undefined = error
  const hookRef = useRef<HTMLDivElement>(null);

  /* -------------------------------------------------------------- */
  /*  Lazy-generate thumbnail when card scrolls into view           */
  /* -------------------------------------------------------------- */
  useEffect(() => {
    const el = hookRef.current;
    if (!el) return;

    const io = new IntersectionObserver(
      async ([entry], obs) => {
        if (!entry.isIntersecting) return;
        obs.disconnect();

        try {
          const pdf = await pdfjs.getDocument(doc.href).promise;
          const page = await pdf.getPage(1);

          const TARGET_W = 300;
          const v1 = page.getViewport({ scale: 1 });
          const v2 = page.getViewport({ scale: TARGET_W / v1.width });

          const canvas = document.createElement('canvas');
          canvas.width = v2.width;
          canvas.height = v2.height;

          await page.render({ canvasContext: canvas.getContext('2d')!, viewport: v2 }).promise;
          setThumbUrl(canvas.toDataURL('image/png'));
        } catch (err) {
          console.warn('Thumbnail generation failed:', err);
          setThumbUrl(undefined);     // so we show the fallback icon
        }
      },
      { rootMargin: '200px' }
    );

    io.observe(el);
    return () => io.disconnect();
  }, [doc.href]);

  /* -------------------------------------------------------------- */
  /*  Event handlers                                                */
  /* -------------------------------------------------------------- */
  const like = async () => { setLikes(v => v + 1); await fetch(`/api/documents/${doc.id}/like`, { method: 'POST' }); };
  const viewed = () => { setViews(v => v + 1); fetch(`/api/documents/${doc.id}/view`, { method: 'POST' }); };
  const share = () => {
    navigator.clipboard
      .writeText(`${location.origin}${doc.href.startsWith('/') ? '' : '/'}${doc.href}`)
      .then(() => alert('Link copied to clipboard!'));
  };
  const saveTags = async () => {
    const cleaned = tagDraft.split(',').map(t => t.trim()).filter(Boolean);
    await fetch(`/api/documents/${doc.id}/tags`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tags: cleaned }),
    });
    setTagsOpen(false);
  };

  /* -------------------------------------------------------------- */
  /*  Render                                                        */
  /* -------------------------------------------------------------- */
  return (
    <div className="graph-system-card">
      {/* ---------- thumbnail + link ---------- */}
      <a
        href={doc.href}
        target="_blank"
        rel="noopener noreferrer"
        onClick={viewed}
        className="graph-system-card-link"
      >
        <div className="card-image-container" ref={hookRef}>
          {thumbUrl ? (
            <img src={thumbUrl} alt={doc.title} className="card-image" />
          ) : thumbUrl === undefined ? (
            <div className="w-full h-full flex items-center justify-center bg-gray-200">
              <ImageOff className="w-6 h-6 text-gray-500" />
            </div>
          ) : (
            <div className="w-full h-full animate-pulse bg-gray-100" />
          )}
        </div>
      </a>

      {/* ---------- text & controls ---------- */}
      <div className="card-content-container space-y-3">
        <h2 className="card-title">{doc.title}</h2>
        {doc.description && <p className="card-description">{doc.description}</p>}

        <div className="flex flex-wrap items-center gap-3 text-sm">
          <Button size="sm" variant="ghost" onClick={like}>
            <Heart className="w-4 h-4 mr-1" /> {likes}
          </Button>

          <span className="flex items-center">
            <Eye className="w-4 h-4 mr-1" /> {views}
          </span>

          <Button size="sm" variant="ghost" onClick={share}>
            <Share2 className="w-4 h-4 mr-1" /> Share
          </Button>

          <Button size="sm" variant="ghost" onClick={() => setTagsOpen(o => !o)}>
            <Tag className="w-4 h-4 mr-1" /> Tags
          </Button>
        </div>

        {tagsOpen && (
          <div className="space-y-2 pt-2">
            <input
              value={tagDraft}
              onChange={e => setTagDraft(e.target.value)}
              className="w-full border rounded px-2 py-1 text-sm"
              placeholder="comma,separated,tags"
            />
            <Button size="sm" className="w-full" onClick={saveTags}>
              Save Tags
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
