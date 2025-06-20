import React from 'react';
import { promises as fs } from 'fs';
import path from 'path';
import InteractiveSequenceView from '@/app/models/[slug]/InteractiveSequenceView';
import model11Data from '@/data/model-11-simulations.json';

const Model11SequenceDisplay = async () => {
  const { scriptsFolder, simulations } = model11Data;
  const folder = scriptsFolder.replace(/^\/+|\/+$/g, '');

  const sequenceData = await Promise.all(
    simulations.map(async sim => {
      // load the .py
      const scriptPath = path.join(process.cwd(), 'public', folder, `${sim.id}.py`);
      let script = '# ERROR: could not load script';
      try {
        script = await fs.readFile(scriptPath, 'utf-8');
      } catch { }

      // build absolute URLs for up to 4 images
      const images = sim.images || [];
      const [img0, img1, img2, img3] = images;
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

  return <InteractiveSequenceView sequenceData={sequenceData} />;
};

export default Model11SequenceDisplay;
