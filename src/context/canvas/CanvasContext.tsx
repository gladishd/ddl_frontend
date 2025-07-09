// The CanvasContext serves as the central state machine for the Graph Virtual Machine (GVM) editor.
// It manages the complete set of graph elements—Cells (nodes), Links (edges), and TRAPHs (groups)—
// and provides a stable, transactional API for their manipulation. Every function here represents
// a reversible or atomic operation on the GVM's persistent groundplane.
'use client';

import React, { createContext, useState, useCallback, useEffect, ReactNode, useMemo } from 'react';
import { Node, Edge, OnNodesChange, OnEdgesChange, OnConnect, applyNodeChanges, applyEdgeChanges, addEdge, Connection, NodeChange, EdgeChange } from 'reactflow';
import { Situation } from '@/types/canvas/Situation';
import { Choice } from '@/types/canvas/Choice';
import { Group } from '@/types/canvas/Group';
import { Key } from '@/types/canvas/Key';
import { placeholderSituations, placeholderGroups, placeholderKeys } from '@/utils/placeholder-data';

const LOCAL_STORAGE_KEY = 'daedalus-groundplane-state';

// --- Context Definition ---
interface CanvasContextType {
  nodes: Node[];
  onNodesChange: OnNodesChange;
  edges: Edge[];
  onEdgesChange: OnEdgesChange;
  onConnect: OnConnect;
  createSituationAndNode: (position: { x: number, y: number }) => void;
  updateSituationAndNode: (id: string, payload: Partial<Situation>) => void;
  deleteSituationAndNode: (id: string) => void;
  createChoiceAndEdge: (sourceSituationId: string) => void;
  updateChoiceAndEdge: (id: string, payload: Partial<Choice>) => void;
  deleteChoiceAndEdge: (id: string) => void;
  saveState: () => void;
  resetState: () => void;
  loading: boolean;
  canvasTitle: string;
  onNodeClick: (event: React.MouseEvent, node: Node) => void;
  onEdgeClick: (event: React.MouseEvent, edge: Edge) => void;
  onCanvasClick: () => void;
  selectedSituation: Situation | null;
  selectedChoice: Choice | null;
  selectedEdgeId: string | null;
  selectedGroup: Group | null;
  getSituation: (id: string) => Situation | undefined;
  getChoice: (id: string) => Choice | undefined;
  [key: string]: any;
}

export const CanvasContext = createContext<CanvasContextType>({} as CanvasContextType);

export const CanvasProvider = ({ children }: { children: ReactNode }) => {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [situations, setSituations] = useState<Situation[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [keys, setKeys] = useState<Key[]>([]);
  const [canvasTitle, setCanvasTitle] = useState('Daedalus Groundplane');
  const [loading, setLoading] = useState(true);
  const [selectedSituation, setSelectedSituation] = useState<Situation | null>(null);
  const [selectedChoice, setSelectedChoice] = useState<Choice | null>(null);
  const [selectedEdgeId, setSelectedEdgeId] = useState<string | null>(null);
  const [selectedGroup, setSelectedGroup] = useState<Group | null>(null);
  const [activeEditTab, setActiveEditTab] = useState('1');

  const saveState = useCallback(() => {
    try {
      const flow = { nodes, edges, situations, groups, keys };
      localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(flow));
    } catch (error) {
      console.error('Failed to save GVM state:', error);
    }
  }, [nodes, edges, situations, groups, keys]);

  useEffect(() => {
    if (!loading) {
      saveState();
    }
  }, [nodes, edges, situations, groups, keys, loading, saveState]);

  const loadInitialState = useCallback((isReset = false) => {
    setLoading(true);
    try {
      const savedState = !isReset ? localStorage.getItem(LOCAL_STORAGE_KEY) : null;
      if (savedState) {
        const restoredFlow = JSON.parse(savedState);
        setSituations(restoredFlow.situations || []);
        setGroups(restoredFlow.groups || []);
        setKeys(restoredFlow.keys || []);
        setNodes(restoredFlow.nodes || []);
        setEdges(restoredFlow.edges || []);
      } else {
        const initialSituations = placeholderSituations;
        const initialGroups = placeholderGroups;
        const initialKeys = placeholderKeys;
        setSituations(initialSituations);
        setGroups(initialGroups);
        setKeys(initialKeys);

        const initialNodes: Node[] = initialSituations.map(s => ({
          id: s._id, type: 'situation', position: s.position,
          data: { label: s.title, endpointType: s.isStart ? 'start' : s.isEnd ? 'end' : undefined },
        }));

        const allChoices: Choice[] = initialSituations.flatMap(s => s.choices || []);
        const initialEdges: Edge[] = allChoices.map(c => ({
          id: c._id, source: c.situation, target: c.nextSituation,
          type: 'choice', data: { label: c.title },
        }));

        setNodes(initialNodes);
        setEdges(initialEdges);
      }
    } catch (error) {
      console.error('Failed to initialize GVM state:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  const resetState = useCallback(() => {
    localStorage.removeItem(LOCAL_STORAGE_KEY);
    loadInitialState(true);
  }, [loadInitialState]);

  useEffect(() => {
    loadInitialState();
  }, [loadInitialState]);

  const getSituation = useCallback((id: string) => situations.find(s => s._id === id), [situations]);
  const getChoice = useCallback((id: string) => situations.flatMap(s => s.choices || []).find(c => c._id === id), [situations]);

  const updateSituationAndNode = useCallback((id: string, payload: Partial<Situation>) => {
    setSituations(prev => prev.map(s => (s._id === id ? { ...s, ...payload } : s)));
    setNodes(prev => prev.map(n => {
      if (n.id === id) {
        const data = { ...n.data };
        if (payload.title !== undefined) data.label = payload.title;
        return { ...n, data, position: payload.position ?? n.position };
      }
      return n;
    }));
  }, []);

  const onNodesChange: OnNodesChange = useCallback((changes) => {
    setNodes((nds) => applyNodeChanges(changes, nds));
    changes.forEach((change: NodeChange) => {
      if (change.type === 'position' && change.position) {
        updateSituationAndNode(change.id, { position: change.position });
      }
    });
  }, [updateSituationAndNode]);

  const deleteSituationAndNode = useCallback((id: string) => {
    setEdges(eds => eds.filter(e => e.source !== id && e.target !== id));
    setSituations(prev => prev.filter(s => s._id !== id));
    setNodes(prev => prev.filter(n => n.id !== id));
    setSituations(prev => prev.map(s => ({
      ...s,
      choices: s.choices.filter(c => c.nextSituation !== id)
    })));
    setSelectedSituation(null);
  }, []);

  const deleteChoiceAndEdge = useCallback((choiceId: string) => {
    setSituations(prev => prev.map(s => ({
      ...s,
      choices: s.choices.filter(c => c._id !== choiceId)
    })));
    setEdges(eds => eds.filter(e => e.id !== choiceId));
    setSelectedChoice(null);
    setSelectedEdgeId(null);
  }, []);

  const onEdgesChange: OnEdgesChange = useCallback((changes) => {
    setEdges((prevEdges) => applyEdgeChanges(changes, prevEdges));
    changes.forEach((change) => {
      if (change.type === 'remove') {
        deleteChoiceAndEdge(change.id);
      }
    });
  }, [deleteChoiceAndEdge]);

  const updateChoiceAndEdge = useCallback((id: string, payload: Partial<Choice>) => {
    setSituations(prev => prev.map(s => ({
      ...s,
      choices: s.choices.map(c => c._id === id ? { ...c, ...payload } : c)
    })));
    setEdges(eds => eds.map(e => {
      if (e.id === id) {
        const data = { ...e.data };
        if (payload.title !== undefined) data.label = payload.title;
        return { ...e, target: payload.nextSituation ?? e.target, data };
      }
      return e;
    }));
  }, []);

  const createChoiceAndEdge = useCallback((sourceSituationId: string) => {
    const newId = `link-${sourceSituationId}-${Date.now()}`;
    const newChoice: Choice = {
      _id: newId, title: 'New Link', situation: sourceSituationId, nextSituation: sourceSituationId
    };
    const newEdge: Edge = {
      id: newId, source: sourceSituationId, target: sourceSituationId, type: 'choice', data: { label: newChoice.title }
    };
    setSituations(prev => prev.map(s => s._id === sourceSituationId ? { ...s, choices: [...s.choices, newChoice] } : s));
    setEdges(eds => addEdge(newEdge, eds));
  }, []);

  const onConnect: OnConnect = useCallback((connection: Connection) => {
    const { source, target } = connection;
    if (!source || !target) return;

    const id = `link-${source}-${target}-${Date.now()}`;
    const newChoice: Choice = { _id: id, title: 'New Link', situation: source, nextSituation: target };
    const newEdge: Edge = { id, source, target, type: 'choice', data: { label: newChoice.title } };

    setSituations(prev => prev.map(s => s._id === source ? { ...s, choices: [...s.choices, newChoice] } : s));
    setEdges(eds => addEdge(newEdge, eds));
  }, []);

  const createSituationAndNode = useCallback((position: { x: number; y: number }) => {
    const id = `cell-${Date.now()}`;
    const newSituation: Situation = {
      _id: id, title: 'New Cell', text: '', isStart: false, isEnd: false, position, choices: []
    };
    const newNode: Node = {
      id, type: 'situation', position, data: { label: newSituation.title },
    };
    setSituations(s => [...s, newSituation]);
    setNodes(n => [...n, newNode]);
  }, []);

  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedSituation(getSituation(node.id) || null);
    setSelectedChoice(null);
    setSelectedEdgeId(null);
    setSelectedGroup(null);
    setActiveEditTab('1');
  }, [getSituation]);

  const onEdgeClick = useCallback((event: React.MouseEvent, edge: Edge) => {
    setSelectedChoice(getChoice(edge.id) || null);
    setSelectedEdgeId(edge.id);
    setSelectedSituation(null);
    setSelectedGroup(null);
    setActiveEditTab('1');
  }, [getChoice]);

  const onCanvasClick = useCallback(() => {
    setSelectedSituation(null);
    setSelectedChoice(null);
    setSelectedEdgeId(null);
    setSelectedGroup(null);
  }, []);

  const contextValue = useMemo(() => ({
    nodes, onNodesChange, edges, onEdgesChange, onConnect,
    createSituationAndNode, updateSituationAndNode, deleteSituationAndNode,
    createChoiceAndEdge, updateChoiceAndEdge, deleteChoiceAndEdge,
    saveState, resetState, loading, canvasTitle,
    onNodeClick, onEdgeClick, onCanvasClick,
    selectedSituation, selectedChoice, selectedEdgeId, selectedGroup,
    situations, groups, keys, getSituation, getChoice, activeEditTab, setActiveEditTab
  }), [
    nodes, onNodesChange, edges, onEdgesChange, onConnect,
    createSituationAndNode, updateSituationAndNode, deleteSituationAndNode,
    createChoiceAndEdge, updateChoiceAndEdge, deleteChoiceAndEdge,
    saveState, resetState, loading, canvasTitle, onNodeClick, onEdgeClick,
    onCanvasClick, selectedSituation, selectedChoice, selectedEdgeId, selectedGroup,
    situations, groups, keys, getSituation, getChoice, activeEditTab
  ]);

  return (
    <CanvasContext.Provider value={contextValue}>
      {children}
    </CanvasContext.Provider>
  );
};