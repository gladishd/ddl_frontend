// A Group represents a 'TRAPH' (TRee-grAPH) or 'Hypercell'—a logical or physical
// grouping of Cells. This structure is fundamental to providing segregation, confinement,
// and hierarchical management within the fabric.
import { Situation } from "./Situation";

export interface Group {
  _id: string;
  title: string;
  description?: string;
  image?: string;
  audio?: string;
  color?: string;
  situations: Situation[];
  isDefault: boolean;
}