// A Choice represents a 'Link' or 'Interaction' between Cells. It is not merely
// a passive channel but an active, stateful agent that mediates causality and
// enforces atomic delivery guarantees.
export interface Choice {
  _id: string;
  title: string;
  nextSituation: string; // The ID of the target Cell
  situation: string; // The ID of the source Cell
  choiceType?: 'hint' | 'normal';
  showIfKey?: string; // ID of a Key that enables this interaction
  hideIfKey?: string; // ID of a Key that disables this interaction
}