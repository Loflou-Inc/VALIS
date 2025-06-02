import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { ChatInterface } from './ChatInterface';
import { SystemDiagnostics } from './SystemDiagnostics';
import { ConfigurationViewer } from './ConfigurationViewer';
import { valisApi } from '@/lib/api';
import type { PersonaInfo } from '@/types';

type ViewMode = 'chat' | 'diagnostics' | 'configuration';

export function MainLayout() {
  const [selectedPersona, setSelectedPersona] = useState<PersonaInfo | null>(null);
  const [currentSession, setCurrentSession] = useState<string>('');
  const [viewMode, setViewMode] = useState<ViewMode>('chat');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // Generate session ID if none exists
  React.useEffect(() => {
    if (!currentSession) {
      const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      setCurrentSession(sessionId);
    }
  }, [currentSession]);

  // Fetch system health for header status
  const { data: healthData, isLoading: healthLoading } = useQuery({
    queryKey: ['health'],
    queryFn: valisApi.getHealth,
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // Fetch personas for sidebar
  const { data: personas = [], isLoading: personasLoading } = useQuery({
    queryKey: ['personas'],
    queryFn: valisApi.getPersonas,
  });

  // Auto-select first persona if none selected
  React.useEffect(() => {
    if (!selectedPersona && personas.length > 0) {
      setSelectedPersona(personas[0]);
    }
  }, [personas, selectedPersona]);

  const handlePersonaSelect = (persona: PersonaInfo) => {
    setSelectedPersona(persona);
    // Generate new session when switching personas
    const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setCurrentSession(sessionId);
  };

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <Header
        healthStatus={healthData?.status || 'unknown'}
        isLoading={healthLoading}
        viewMode={viewMode}
        onViewModeChange={setViewMode}
        onToggleSidebar={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <Sidebar
          personas={personas}
          selectedPersona={selectedPersona}
          onPersonaSelect={handlePersonaSelect}
          isLoading={personasLoading}
          collapsed={sidebarCollapsed}
        />

        {/* Main Content */}
        <main className="flex-1 flex flex-col overflow-hidden">
          {viewMode === 'chat' ? (
            <ChatInterface
              selectedPersona={selectedPersona}
              sessionId={currentSession}
            />
          ) : viewMode === 'diagnostics' ? (
            <SystemDiagnostics />
          ) : (
            <ConfigurationViewer />
          )}
        </main>
      </div>
    </div>
  );
}