'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Heart, Eye, Tag, Share2, ImageOff, X as CloseIcon } from 'lucide-react';
import { pdfjs } from 'react-pdf';
import type { DocumentRecord } from '@/types/Document';
import { Button } from '@/components/ui/button';
// ──────────────────────────────────────────────────────────────
// Quick helper – tells us if a path looks like an image
// (add /webp /svg etc. if you store them)
// ──────────────────────────────────────────────────────────────
const isImageFile = (href: string) =>
  [".png", ".jpg", ".jpeg", ".gif", ".webp"].some(ext =>
    href.toLowerCase().endsWith(ext),
  );

if (typeof window !== 'undefined' && !pdfjs.GlobalWorkerOptions.workerSrc) {
  pdfjs.GlobalWorkerOptions.workerSrc = new URL(
    'pdfjs-dist/build/pdf.worker.min.mjs',
    import.meta.url,
  ).toString();
}

type Props = { doc: DocumentRecord };

export default function DocumentCard({ doc }: Props) {
  const [likes, setLikes] = useState<number>(doc.likes);
  const [views, setViews] = useState<number>(doc.views);
  const [tags, setTags] = useState<string[]>(doc.tags);
  const [tagsOpen, setTagsOpen] = useState<boolean>(false);
  const [newTag, setNewTag] = useState<string>('');

  const [thumbUrl, setThumbUrl] = useState<string | null>(null);
  const hookRef = useRef<HTMLDivElement>(null);
  const tagsInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const el = hookRef.current;
    if (!el) return;

    const io = new IntersectionObserver(
      async ([entry], obs) => {
        if (!entry.isIntersecting) return;
        obs.disconnect();

        /* ── 1️⃣ If it’s an image, just use the file itself ─────────── */
        if (isImageFile(doc.href)) {
          setThumbUrl(doc.href);
          return;
        }

        /* ── 2️⃣ Otherwise fall back to the current PDF-render path ──── */
        try {
          const pdf = await pdfjs.getDocument(doc.href).promise;
          const page = await pdf.getPage(1);
          const W = 300;
          const vBase = page.getViewport({ scale: 1 });
          const view = page.getViewport({ scale: W / vBase.width });

          const canvas = document.createElement('canvas');
          canvas.width = view.width;
          canvas.height = view.height;
          await page.render({ canvasContext: canvas.getContext('2d')!, viewport: view }).promise;

          setThumbUrl(canvas.toDataURL('image/png'));
        } catch (err) {
          console.warn('Thumbnail generation failed:', err);
          setThumbUrl(null);
        }
      },
      { rootMargin: '200px' }
    );

    io.observe(el);
    return () => io.disconnect();
  }, [doc.href]);

  const like = async () => { setLikes(v => v + 1); await fetch(`/api/documents/${doc.id}/like`, { method: 'POST' }); };
  const viewed = () => { setViews(v => v + 1); fetch(`/api/documents/${doc.id}/view`, { method: 'POST' }); };
  const share = () => {
    navigator.clipboard
      .writeText(`${location.origin}${doc.href.startsWith('/') ? '' : '/'}${doc.href}`)
      .then(() => alert('Link copied to clipboard!'));
  };

  const handleAddTag = async (tagToAdd: string) => {
    const cleaned = tagToAdd.trim();
    if (cleaned && !tags.includes(cleaned)) {
      const newTags = [...tags, cleaned];
      setTags(newTags);
      setNewTag('');
      await saveTags(newTags);
    }
  };

  const handleRemoveTag = async (tagToRemove: string) => {
    const newTags = tags.filter(t => t !== tagToRemove);
    setTags(newTags);
    await saveTags(newTags);
  };

  const saveTags = async (tagsToSave: string[]) => {
    await fetch(`/api/documents/${doc.id}/tags`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tags: tagsToSave }),
    });
  };

  return (
    <div className="graph-system-card">
      <a href={doc.href} target="_blank" rel="noopener noreferrer" onClick={viewed} className="graph-system-card-link">
        <div className="card-image-container" ref={hookRef}>
          {thumbUrl ? (
            <img src={thumbUrl} alt={doc.title} className="card-image" />
          ) : thumbUrl === undefined ? ( /*  still rendering  */
            <div className="w-full h-full flex items-center justify-center bg-gray-200">
              <ImageOff className="w-6 h-6 text-gray-500" />
            </div>
          ) : (
            <div className="w-full h-full animate-pulse bg-gray-100" />
          )}
        </div>
      </a>

      <div className="card-content-container space-y-3">
        <h2 className="card-title">{doc.title}</h2>
        {doc.description && <p className="card-description">{doc.description}</p>}

        <div className="flex flex-wrap items-center gap-3 text-sm">
          <Button size="sm" variant="ghost" onClick={like}><Heart className="w-4 h-4 mr-1" /> {likes}</Button>
          <span className="flex items-center"><Eye className="w-4 h-4 mr-1" /> {views}</span>
          <Button size="sm" variant="ghost" onClick={share}><Share2 className="w-4 h-4 mr-1" /> Share</Button>
          <Button size="sm" variant="ghost" onClick={() => setTagsOpen(o => !o)}><Tag className="w-4 h-4 mr-1" /> Tags</Button>
        </div>

        {tagsOpen && (
          <div className="tag-editor-container" onClick={() => tagsInputRef.current?.focus()}>
            <div className="tag-pill-container">
              {tags.map(tag => (
                <div key={tag} className="tag-pill">
                  <span>{tag}</span>
                  <button onClick={() => handleRemoveTag(tag)} className="tag-pill-remove"><CloseIcon size={12} /></button>
                </div>
              ))}
              <input
                ref={tagsInputRef}
                value={newTag}
                onChange={e => setNewTag(e.target.value)}
                onKeyDown={e => {
                  if (e.key === ',' || e.key === 'Enter') {
                    e.preventDefault();
                    handleAddTag(newTag);
                  }
                }}
                className="tag-input"
                placeholder="Add a tag..."
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}