import React, { useContext, useState, useEffect } from 'react';
import { DragDropContext, Droppable, Draggable, DropResult } from '@hello-pangea/dnd';
import styles from './styles/ChoicesList.module.css';
import { CanvasContext } from '@/context/canvas/CanvasContext';
import { Choice } from '@/types/canvas/Choice';

// This component renders the set of outgoing Links (Choices) for a selected Cell.
// The ability to reorder these links via drag-and-drop is a direct manipulation of the
// GVM, allowing the user to define the preferential order of causal paths originating
// from the Cell, without relying on ambiguous or probabilistic routing.
const ChoicesList: React.FC = () => {
    const { selectedSituation, updateSituationAndNode, getChoice, setActiveEditTab, loading } = useContext(CanvasContext);
    const [displayChoices, setDisplayChoices] = useState<Choice[]>([]);

    useEffect(() => {
        setDisplayChoices(selectedSituation?.choices || []);
    }, [selectedSituation]);

    const handleDragEnd = async (result: DropResult) => {
        if (!result.destination) return;
        if (!selectedSituation?._id || loading) return;

        const reorderedChoices = Array.from(displayChoices);
        const [removed] = reorderedChoices.splice(result.source.index, 1);
        reorderedChoices.splice(result.destination.index, 0, removed);

        setDisplayChoices(reorderedChoices);
        const reorderedChoiceIds = reorderedChoices.map(choice => choice._id);

        try {
            await updateSituationAndNode(selectedSituation._id, { choices: reorderedChoiceIds });
        } catch (error) {
            console.error("Error updating choice order:", error);
            setDisplayChoices(selectedSituation?.choices || []);
        }
    };

    const handleChoiceClick = async (choiceId: string) => {
        if (loading) return;
        try {
            await getChoice(choiceId);
            if(setActiveEditTab) setActiveEditTab('1');
        } catch (error) {
            console.error("Error fetching choice:", error);
        }
    };

    return (
        <DragDropContext onDragEnd={handleDragEnd}>
            <Droppable droppableId="droppable-choices">
                {(provided) => (
                    <div ref={provided.innerRef} {...provided.droppableProps} className={styles.choicesContainer}>
                        {displayChoices.length > 0 ? (
                            displayChoices.map((choice, index) => (
                                <Draggable key={choice._id} draggableId={choice._id} index={index} isDragDisabled={loading}>
                                    {(provided, snapshot) => (
                                        <div
                                            ref={provided.innerRef}
                                            {...provided.draggableProps}
                                            {...provided.dragHandleProps}
                                            className={`${styles.choiceItem} ${snapshot.isDragging ? styles.dragging : ''}`}
                                            onClick={() => handleChoiceClick(choice._id)}
                                        >
                                            <div className={styles.choiceTitle}>{choice.title || 'Untitled'}</div>
                                            <div className={styles.nextSituationTitle}>
                                                <span className={styles.linkLabel}>Links to:</span>
                                                {(choice.nextSituation as any)?.title || 'Unlinked'}
                                            </div>
                                        </div>
                                    )}
                                </Draggable>
                            ))
                        ) : (
                            !loading && <p className={styles.noChoices}>No outgoing Links defined.</p>
                        )}
                        {provided.placeholder}
                    </div>
                )}
            </Droppable>
        </DragDropContext>
    );
};

export default ChoicesList;