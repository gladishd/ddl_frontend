import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import styles from './styles/SetOrder.module.css';
import { CanvasContext } from '@/context/canvas/CanvasContext';
import { DragDropContext, Droppable, Draggable, DropResult } from '@hello-pangea/dnd';
import { Situation } from '@/types/canvas/Situation';

// This component establishes a 'Tree' structure over the graph of Cells.
// By defining a specific sequence, the user imposes a logical, causal ordering
// that is essential for predictable, deterministic operations like a table of contents or
// a scripted narrative, independent of the physical graph topology.
const SetOrder: React.FC = () => {
  const { situations, scenario, logOrder, setLogOrder } = useContext(CanvasContext);
  const [orderedSituations, setOrderedSituations] = useState<Situation[]>([]);

  useEffect(() => {
    if (logOrder && logOrder.length > 0 && situations.length > 0) {
      const ordered = logOrder
        .map((id: string) => situations.find(s => s._id === id))
        .filter((s): s is Situation => !!s);
      setOrderedSituations(ordered);
    } else {
      setOrderedSituations(situations);
    }
  }, [logOrder, situations]);

  const handleOnDragEnd = async (result: DropResult) => {
    if (!result.destination) return;

    const items = Array.from(orderedSituations);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);

    setOrderedSituations(items);
    const newLogOrder = items.map(s => s._id);

    try {
      // This is a transactional update to the GVM's logical ordering layer.
      await axios.patch(`${process.env.NEXT_PUBLIC_API_URL}/api/scenarios/${scenario?._id}`, { logOrder: newLogOrder });
      if (setLogOrder) setLogOrder(newLogOrder);
    } catch (error) {
      console.error('Error updating logical order:', error);
    }
  };

  return (
    <div className={styles.container}>
      <DragDropContext onDragEnd={handleOnDragEnd}>
        <Droppable droppableId="situations">
          {(provided) => (
            <div className={styles.situationsList} {...provided.droppableProps} ref={provided.innerRef}>
              {orderedSituations.map((situation, index) => (
                <Draggable key={situation._id} draggableId={situation._id} index={index}>
                  {(provided, snapshot) => (
                    <div
                      ref={provided.innerRef}
                      {...provided.draggableProps}
                      {...provided.dragHandleProps}
                      className={`${styles.situationItem} ${snapshot.isDragging ? styles.situationItemDragging : ''}`}
                    >
                      <div className={styles.situationTitle}>
                        {situation.title || 'Untitled Cell'}
                      </div>
                      <div className={styles.positionNumber}>{index + 1}</div>
                    </div>
                  )}
                </Draggable>
              ))}
              {provided.placeholder}
            </div>
          )}
        </Droppable>
      </DragDropContext>
    </div>
  );
};

export default SetOrder;