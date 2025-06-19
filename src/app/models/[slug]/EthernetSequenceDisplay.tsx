import React from 'react';
import { promises as fs } from 'fs';
import path from 'path';
import InteractiveSequenceView from './InteractiveSequenceView';

// Metadata now points at files in /public/scripts/ethernet-sequence
const sequenceMetadata = [
  {
    title: 'Model 1: Pure & Slotted ALOHA (`model1_aloha.py`)',
    scriptPath: 'scripts/ethernet-sequence/model1_aloha.py',
    output: `Protocol: csma\nOffered load G = 0.050\nThroughput S = 0.049 pkts/unit time`,
    image: '/models/comprehensive.py.png'
  },
  {
    title: 'Model 2: TCP Handshake over Ethernet (`model2_tcp_handshake.py`)',
    scriptPath: 'scripts/ethernet-sequence/model2_tcp_handshake.py',
    output: null,
    image: '/models/comprehensive1.py.png'
  },
  {
    title: 'Model 3: Acknowledged Data Transfer (`model3_acknowledged_transfer.py`)',
    scriptPath: 'scripts/ethernet-sequence/model3_acknowledged_transfer.py',
    output: null,
    image: '/models/comprehensive2.py.png'
  },
  {
    title: 'Model 4: Contention Simulation with GIF Export (`model4_contention_gif.py`)',
    scriptPath: 'scripts/ethernet-sequence/model4_contention_gif.py',
    output: `--- Daedaelus Ethernet Contention Simulation ---\nMode: CSMA_CD, Stations: 10, Link Speed: 3.0 Mbps\n--- Simulation Results ---\nTotal time simulated: 0.5000 s\nThroughput: 2.9901 Mbps\nChannel Efficiency: 99.6693%`,
    image: '/models/comprehensive3.py_ethernet_contention.gif'
  },
  {
    title: 'Model 5: Acknowledged Protocol Simulation (`model5_acknowledged_protocol.py`)',
    scriptPath: 'scripts/ethernet-sequence/model5_acknowledged_protocol.py',
    output: `--- Daedaelus Acknowledged Ethernet Simulation ---\nApplication Goodput: 2.8055 Mbps\nChannel Efficiency (Busy Time): 99.3607%`,
    image: '/models/comprehensive4.gif'
  },
  {
    title: 'Model 6: Full Network Simulation (`model6_full_network.py`)',
    scriptPath: 'scripts/ethernet-sequence/model6_full_network.py',
    output: `=== Simulation Results ===\nSimulated time: 551 packets in 0.04 seconds\nThroughput: -4.24 packets/sec\nDelivery ratio: -76.95%\nCollision rate: 43.56%`,
    image: '/models/comprehensive5.py.png',
    secondImage: '/models/comprehensive5_2.py.png'
  },
];

const EthernetSequenceDisplay = async () => {
  // All scripts are now under public/, so we join process.cwd(), 'public', scriptPath
  const sequenceData = await Promise.all(
    sequenceMetadata.map(async (meta) => {
      const filePath = path.join(process.cwd(), 'public', meta.scriptPath);
      try {
        const scriptContent = await fs.readFile(filePath, 'utf-8');
        return {
          ...meta,
          script: scriptContent,
        };
      } catch (error) {
        console.error(`Error reading script for ${meta.title}:`, error);
        return {
          ...meta,
          script: `# ERROR: Could not load script from /${meta.scriptPath}`,
        };
      }
    })
  );

  return <InteractiveSequenceView sequenceData={sequenceData} />;
};

export default EthernetSequenceDisplay;
