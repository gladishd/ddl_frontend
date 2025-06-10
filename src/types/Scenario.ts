// Represents the metadata for a single Graph System or Digital Twin.
// This structure defines its identity, creator, and how it is presented and interacted with.

export interface Scenario {
  _id: string;
  title: string;
  description?: string;
  image?: string;
  creator: {
    _id: string;
    username: string;
  };
  views: number;
  likedBy: string[];
  isPublished: boolean;
  isHidden: boolean;
  tags: string[];
  createdAt: string;
  updatedAt: string;
}