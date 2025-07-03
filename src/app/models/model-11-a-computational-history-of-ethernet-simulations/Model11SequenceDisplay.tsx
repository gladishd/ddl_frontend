'use client';

import React, { useEffect, useState } from 'react';
import InteractiveSequenceView from '@/app/models/[slug]/InteractiveSequenceView';
import model11Data from '@/data/model-11-simulations.json';

type SequenceItem = {
  title: string;
  script: string;
  output: string | null;
  image: string;
  secondImage?: string;
  thirdImage?: string;
  fourthImage?: string;
};

const Model11SequenceDisplay: React.FC = () => {
  const [sequenceData, setSequenceData] = useState<SequenceItem[]>([]);
  const { scriptsFolder, simulations } = model11Data;
  const folder = scriptsFolder.replace(/^\/+|\/+$/g, '');

  useEffect(() => {
    (async () => {
      const items = await Promise.all(
        simulations.map(async (sim) => {
          const scriptUrl = `${process.env.NEXT_PUBLIC_BASE_URL || ''}/${folder}/${sim.id}.py`;
          let script = '# ERROR: could not load script';
          try {
            const res = await fetch(scriptUrl);
            if (res.ok) {
              script = await res.text();
            }
          } catch (e) {
            console.error('Failed to fetch', scriptUrl, e);
          }

          const [img0, img1, img2, img3] = sim.images || [];
          return {
            title: sim.title,
            script,
            output: sim.output || null,
            image: img0 ? `/${folder}/${img0}` : '',
            secondImage: img1 ? `/${folder}/${img1}` : undefined,
            thirdImage: img2 ? `/${folder}/${img2}` : undefined,
            fourthImage: img3 ? `/${folder}/${img3}` : undefined,
          };
        })
      );
      setSequenceData(items);
    })();
  }, [simulations, folder]);

  if (!sequenceData.length) {
    return <div className="p-4 text-center">Loading sequences…</div>;
  }

  return <InteractiveSequenceView sequenceData={sequenceData} />;
};

export default Model11SequenceDisplay;
