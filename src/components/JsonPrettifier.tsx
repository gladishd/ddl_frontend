// This component recursively renders JSON data into an interactive, styled tree.
// It reflects the Daedaelus principle of bringing clarity and structure to complex information,
// transforming raw data into an explorable multiway system of key-value pairs.
"use client";

import React, { useState } from 'react';

interface JsonPrettifierProps {
  data: any;
  initialExpanded?: boolean;
}

const JsonPrettifier: React.FC<JsonPrettifierProps> = ({ data, initialExpanded = false }) => {
  const [expanded, setExpanded] = useState(initialExpanded);

  if (typeof data !== 'object' || data === null) {
    let type = 'null';
    if (typeof data === 'string') type = 'string';
    if (typeof data === 'number') type = 'number';
    if (typeof data === 'boolean') type = 'boolean';

    return <span className={`json-prettifier ${type}`}>{JSON.stringify(data)}</span>;
  }

  const isArray = Array.isArray(data);
  const entries = Object.entries(data);
  const summary = isArray ? `[${entries.length} items]` : `{${entries.length} keys}`;

  return (
    <div className="json-prettifier">
      <span className="collapsible" onClick={() => setExpanded(!expanded)}>
        {summary}
      </span>
      {expanded && (
        <ul>
          {entries.map(([key, value]) => (
            <li key={key}>
              <span className="key">{isArray ? '' : `"${key}": `}</span>
              <JsonPrettifier data={value} initialExpanded={false} />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default JsonPrettifier;