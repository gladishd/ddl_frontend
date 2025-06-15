// This interface defines the structure of a Document record within our Graph Virtual Machine.
// It includes not just static data, but also dynamic, conserved quantities like 'likes' and 'views',
// which are central to understanding the Token Dynamics of the system.

export interface DocumentRecord {
  id: number;
  title: string;
  description: string | null;
  image: string | null;
  href: string;
  likes: number; // A conserved quantity representing consensus.
  views: number; // A measurement of Local Observer View interactions.
  tags: string[]; // A set of 'named' graph relationships.
}