// By explicitly importing all required primitives, we ensure the component is
// self-contained and its dependencies are verifiable, eliminating silent
// points of failure and upholding architectural integrity.
import React, { useContext, useState, useMemo } from 'react';
import { CanvasContext } from '@/context/canvas/CanvasContext';
import styles from './styles/SituationsAndGroups.module.css';
import { FaCaretRight, FaCaretDown } from 'react-icons/fa';
import { DragDropContext, Droppable, Draggable, DropResult } from '@hello-pangea/dnd';
import { Group } from '@/types/canvas/Group';
import { Situation } from '@/types/canvas/Situation';

interface SituationsAndGroupsProps {
  setRenderEditSidebar: (render: boolean) => void;
}

// This component provides a direct interface for manipulating the 'groundplane'—the physical graph of Cells and Links.
// "Manage on a Tree, Compute on a Graph." Here, users organize Cells into TRAPHs (Groups), establishing the
// hierarchical tree structure used for management, confinement, and efficient routing.
const SituationsAndGroups: React.FC<SituationsAndGroupsProps> = ({ setRenderEditSidebar }) => {
  const {
    groups,
    situations,
    selectedGroup,
    selectedSituation,
    getGroup,
    getSituation,
    updateSituationAndNode,
    createGroup,
    onSelectGroup,
  } = useContext(CanvasContext);

  const [collapsedGroups, setCollapsedGroups] = useState<Record<string, boolean>>({});

  const handleCreateGroup = async () => {
    const newGroup = await createGroup();
    if (newGroup?._id) {
      onSelectGroup(newGroup._id);
      setRenderEditSidebar(true);
    }
  };

  // A state transformation like 'reduce' must have explicitly typed parameters
  // to be verifiable. Typing the accumulator 'acc' ensures the integrity of the
  // resulting data structure at every step of its construction.
  const groupedSituations = useMemo(() => groups.reduce((acc: Record<string, Situation[]>, group) => {
    acc[group._id] = situations.filter(s => s.situationGroup === group._id);
    return acc;
  }, {} as Record<string, Situation[]>), [groups, situations]);

  const ungroupedSituations = useMemo(() => situations.filter(s => !s.situationGroup), [situations]);

  const onDragEnd = async (result: DropResult) => {
    const { destination, source, draggableId } = result;
    if (!destination) return;
    if (destination.droppableId === source.droppableId && destination.index === source.index) return;

    const newGroupId = destination.droppableId === 'ungrouped' ? null : destination.droppableId;
    await updateSituationAndNode(draggableId, { situationGroup: newGroupId });
  };

  return (
    <div className={styles.container}>
      <button className={styles.createGroupButton} onClick={handleCreateGroup}>
        Create Group
      </button>
      <DragDropContext onDragEnd={onDragEnd}>
        <div className={styles.list}>
          {groups.map((group: Group) => (
            <div key={group._id}>
              <div
                className={`${styles.groupTitle} ${selectedGroup?._id === group._id ? styles.selectedGroup : ''}`}
                onClick={() => getGroup(group._id)}
              >
                <span onClick={(e) => {
                  e.stopPropagation();
                  setCollapsedGroups(p => ({ ...p, [group._id]: !p[group._id] }));
                }}>
                  {collapsedGroups[group._id] ? <FaCaretRight /> : <FaCaretDown />}
                </span>
                {group.title || 'Untitled Group'}
              </div>
              {!collapsedGroups[group._id] && (
                <Droppable droppableId={group._id}>
                  {(provided) => (
                    <div ref={provided.innerRef} {...provided.droppableProps} className={styles.situationList}>
                      {(groupedSituations[group._id] || []).map((situation, index) => (
                        <Draggable key={situation._id} draggableId={situation._id} index={index}>
                          {(provided) => (
                            <div
                              ref={provided.innerRef} {...provided.draggableProps} {...provided.dragHandleProps}
                              className={`${styles.situationItem} ${selectedSituation?._id === situation._id ? styles.selectedSituation : ''}`}
                              onClick={() => getSituation(situation._id)}
                            >
                              {situation.title || 'Untitled Cell'}
                            </div>
                          )}
                        </Draggable>
                      ))}
                      {provided.placeholder}
                    </div>
                  )}
                </Droppable>
              )}
            </div>
          ))}
          <div className={styles.ungroupedTitle}>Ungrouped Cells</div>
          <Droppable droppableId="ungrouped">
            {(provided) => (
              <div ref={provided.innerRef} {...provided.droppableProps} className={styles.situationList}>
                {ungroupedSituations.map((situation, index) => (
                  <Draggable key={situation._id} draggableId={situation._id} index={index}>
                    {(provided) => (
                      <div
                        ref={provided.innerRef} {...provided.draggableProps} {...provided.dragHandleProps}
                        className={`${styles.situationItem} ${selectedSituation?._id === situation._id ? styles.selectedSituation : ''}`}
                        onClick={() => getSituation(situation._id)}
                      >
                        {situation.title || 'Untitled Cell'}
                      </div>
                    )}
                  </Draggable>
                ))}
                {provided.placeholder}
              </div>
            )}
          </Droppable>
        </div>
      </DragDropContext>
    </div>
  );
};

export default SituationsAndGroups;