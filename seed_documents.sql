-- This script seeds the 'documents' table with the initial set of records.
-- Run this *after* executing 'create_document_features.sql'.

BEGIN;

INSERT INTO documents (title, description, image, href) VALUES
(
  'Packct Spraying',
  'Technical notes on packet-spraying attack simulations',
  'https://images.unsplash.com/photo-...q=80',  -- pick an appropriate image URL
  '/Packct-Spraying.pdf'
),
(
  'Bandwidth Works in Practice, not in Theory',
  'A real-world look at Ethernet performance versus the textbooks.',
  'https://images.unsplash.com/photo-1550745165-9bc0b252726a?auto=format&fit=crop&w=800&q=80',
  '/Bandwidth-Works-in-Practice-not-in-Theory.pdf'
),
(
  'LaTeX File Color Mapping',
  'Mapping macOS tag colors to .tex, .sty, and project files.',
  'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?auto=format&fit=crop&w=800&q=80',
  '/Latex-Files-and-Colors.numbers.pdf'
),
(
  'Ethernet: Distributed Packet Switching',
  'The original 1976 Metcalfe & Boggs Ethernet spec, straight from PARC.',
  'https://images.unsplash.com/photo-1534972195531-d756b9bfa9f2?auto=format&fit=crop&w=800&q=80',
  '/main.pdf'
),
(
  'Bandwidth Works in Practice (June 2025)',
  'June 2025 follow-up on practical throughput studies.',
  'https://images.unsplash.com/photo-1581094794329-c8112a89af10?auto=format&fit=crop&w=800&q=80',
  '/main2.pdf'
),
(
  'Ethernet Spec (Mirror)',
  'Alternate mirror of the classic Metcalfe & Boggs paper.',
  'https://images.unsplash.com/photo-1551836022-d5d88e9218df?auto=format&fit=crop&w=800&q=80',
  '/main3.pdf'
),
(
  'Ethernet Spec (Full PDF)',
  'Yet another copy, just in case — complete and unabridged.',
  'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=800&q=80',
  '/Metcalfe+Boggs.pdf'
),
(
  'NDA – Dean Gladish',
  'Legal agreement governing our collaboration details.',
  'https://images.unsplash.com/photo-1556742031-c6961e8560b0?auto=format&fit=crop&w=800&q=80',
  '/NDA-Dean-Gladish-2025-06-04_23-06.pdf'
),
(
  'OAE Logo',
  'High-resolution vector of the Official Academic Emblem.',
  'https://images.unsplash.com/photo-1529676468690-a0ff4e722963?auto=format&fit=crop&w=800&q=80',
  '/OAE_Logo_copy.pdf'
),
(
  'Fig. 1 – Two-segment Ethernet',
  'Illustration showing dual-segment collision domains.',
  'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=800&q=80',
  '/Omni-Figure-1.pdf'
),
(
  'Reinventing Reliability at L2',
  'Modern take on making Ethernet reliable without extra bandwidth cost.',
  'https://images.unsplash.com/photo-1581091012184-38d3b93dc357?auto=format&fit=crop&w=800&q=80',
  '/Reinventing-Reliability-at-L2.pdf'
),
(
  'Ethernet Template Copy',
  'Yet another template copy — same as “main.pdf.”',
  'https://images.unsplash.com/photo-1573497169428-b8d87734a5a2?auto=format&fit=crop&w=800&q=80',
  '/template_copy.pdf'
),
(
  'Testing the Ethernet Figures',
  'Draft file with experimental diagrams for collision backoff.',
  'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80',
  '/TEST-Ethernet-Figures.pdf'
),
(
  'Computer Systems – Bell, Fuller, Siewiorek',
  'Chapters on systems design, with an Ethernet overview.',
  'https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=800&q=80',
  '/test.pdf'
),
(
  'Welcome Dean – Introduction to Dædælus',
  'The “hello world” of Dædælus — our mission statement.',
  'https://images.unsplash.com/photo-1526401281623-3ad9882883b4?auto=format&fit=crop&w=800&q=80',
  '/Welcome-Dean.pdf'
),
(
  'FAQ – Graph Virtual Machine (GVM)',
  'Frequently asked questions on the design and usage of the Graph Virtual Machine.',
  'https://images.unsplash.com/photo-...q=80',
  '/FAQ-GVM.pdf'
),
(
  'Reversibility & Time-Reversible Computing',
  'Charles H. Bennett’s foundational paper on logical reversibility and thermodynamics of computation.',
  'https://images.unsplash.com/photo-XXXXXX?auto=format&fit=crop&w=800&q=80',
  '/Bennett_Reversibility.pdf'
)
ON CONFLICT (href) DO NOTHING; -- Avoids errors if you run the script multiple times

COMMIT;