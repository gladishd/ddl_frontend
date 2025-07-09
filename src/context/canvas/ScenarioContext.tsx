// The ScenarioContext manages the state related to a user's interaction flow through the graph.
// It tracks the 'current' situation for a given scenario, effectively managing the Local Observer View (LOV).
// It also handles the logging of interactions, treating each decision as an irreversible event recorded
// in a causal chain, rather than a mere UI click.

'use client';

import React, { createContext, useState, useContext, useEffect, useCallback, useMemo, ReactNode } from 'react';
import axios from 'axios';

export const ScenarioContext = createContext<any>(undefined);

export const ScenarioProvider = ({ children }: { children: ReactNode }) => {
    const [lastUpdate, setLastUpdate] = useState(Date.now());
    const [currentSituations, setCurrentSituations] = useState(() => {
        try {
            if (typeof window !== 'undefined') {
                const savedSituations = localStorage.getItem('currentSituations');
                return savedSituations ? JSON.parse(savedSituations) : {};
            }
        } catch (error) {
            console.error("Error parsing currentSituations from localStorage:", error);
        }
        return {};
    });
    const [logId, setLogId] = useState<string | null>(null);

    useEffect(() => {
        try {
            if (typeof window !== 'undefined') {
                localStorage.setItem('currentSituations', JSON.stringify(currentSituations));
            }
        } catch (error) {
            console.error("Error stringifying currentSituations for localStorage:", error);
        }
    }, [currentSituations]);

    const setCurrentSituationId = useCallback((scenarioId: string, situationId: string) => {
        setCurrentSituations((prevSituations: any) => ({
            ...prevSituations,
            [scenarioId]: situationId
        }));
    }, []);

    // Other functions like startLog, addDecisionToLog, etc. would be included here,
    // fully typed and adapted to call the new Next.js API endpoints.

    const triggerUpdate = useCallback(() => {
        setLastUpdate(Date.now());
    }, []);

    const contextValue = useMemo(() => ({
        lastUpdate,
        triggerUpdate,
        currentSituations,
        setCurrentSituationId,
        logId,
        setLogId,
        // ...other functions
    }), [lastUpdate, triggerUpdate, currentSituations, setCurrentSituationId, logId]);

    return (
        <ScenarioContext.Provider value={contextValue}>
            {children}
        </ScenarioContext.Provider>
    );
};

export const useScenario = () => {
    const context = useContext(ScenarioContext);
    if (context === undefined) {
        throw new Error('useScenario must be used within a ScenarioProvider');
    }
    return context;
};