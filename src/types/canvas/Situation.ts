// A Situation represents a 'Cell' in the Daedaelus architecture—a reactive,
// self-contained participant in a global program that holds local state and
// executes reversible transactions.
import { Choice } from "./Choice";

export interface Situation {
  _id: string;
  title: string;
  text: string;
  isStart: boolean;
  isEnd: boolean;
  image?: string;
  audio?: string;
  choices: Choice[];
  situationGroup?: string; // ID of the group (TRAPH) it belongs to
  position: { x: number; y: number };
  fillColor?: string;
  borderColor?: string;
}