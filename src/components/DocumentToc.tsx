import React from 'react';
import { DocumentRecord } from '@/types/Document';
import { Button } from '@/components/ui/button';
import { FaFilePdf } from 'react-icons/fa';

// This component provides a Table of Contents view, a structured representation of the library.
// It reflects the 'Neighbor to Neighbor (N2N) Lattice' principle, where information is managed
// on a tree structure for clarity and efficient access.
interface DocumentTocProps {
  documents: DocumentRecord[];
}

const DocumentToc: React.FC<DocumentTocProps> = ({ documents }) => {
  if (!documents || documents.length === 0) {
    return null; // Render nothing if there are no documents to display
  }

  return (
    <div className="document-toc-container">
      <ul className="document-toc-list">
        {documents.map(doc => (
          <li key={doc.id} className="document-toc-item-wrapper">
            <a
              href={doc.href}
              target="_blank"
              rel="noopener noreferrer"
              className="document-toc-item"
            >
              <FaFilePdf className="toc-icon" />
              <div className="toc-text-content">
                <span className="toc-title">{doc.title}</span>
                {doc.description && <p className="toc-description">{doc.description}</p>}
              </div>
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default DocumentToc;