// This file provides a pre-configured initial state for the GVM groundplane.
// It serves as a stand-in for a persistent backend, allowing for frontend
// development and emulation without a live data source.
import { Situation } from '@/types/canvas/Situation';
import { Group } from '@/types/canvas/Group';
import { Key } from '@/types/canvas/Key';
import { Choice } from '@/types/canvas/Choice';

// --- TRAPHs (Groups) ---
export const placeholderGroups: Group[] = [
  {
    _id: 'group-default',
    title: 'Default TRAPH',
    description: 'Default container for ungrouped Cells.',
    situations: [],
    isDefault: true,
  },
];

// --- Conserved Quantities (Keys) ---
export const placeholderKeys: Key[] = [
  {
    _id: 'key-1',
    name: 'System Access Token',
    description: 'A capability token required for critical operations.',
  },
];

// --- Cells (Situations) and their Links (Choices) ---
const choice1: Choice = {
    _id: 'choice-1-2',
    title: 'Engage',
    situation: 'sit-1',
    nextSituation: 'sit-2',
};

const situation1: Situation = {
    _id: 'sit-1',
    title: 'Initial State',
    text: 'The system is in a stable, equilibrium state. Awaiting interaction.',
    isStart: true,
    isEnd: false,
    position: { x: 250, y: 250 },
    choices: [choice1],
};

const situation2: Situation = {
    _id: 'sit-2',
    title: 'Interaction Received',
    text: 'A token has been received. The state has evolved.',
    isStart: false,
    isEnd: false,
    position: { x: 550, y: 250 },
    choices: [],
};

const situation3: Situation = {
    _id: 'sit-3',
    title: 'Terminal State',
    text: 'The transaction has completed, and the state is now final.',
    isStart: false,
    isEnd: true,
    position: { x: 850, y: 250 },
    choices: [],
};

export const placeholderSituations: Situation[] = [situation1, situation2, situation3];