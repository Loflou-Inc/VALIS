import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { 
  Brain, 
  Star, 
  User, 
  MessageSquare,
  ChevronDown,
  ChevronRight,
  Zap,
  Database
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { valisApi } from '@/lib/api';
import type { PersonaInfo, MemoryLayers } from '@/types';
import { format } from 'date-fns';

interface MemoryDiagnosticsProps {
  selectedPersona: PersonaInfo | null;
  sessionId: string;
  className?: string;
}

export function MemoryDiagnostics({ selectedPersona, sessionId, className }: MemoryDiagnosticsProps) {
  const [expandedLayers, setExpandedLayers] = useState<Record<string, boolean>>({
    core_biography: true,
    canonized_identity: true,
    client_profile: false,
    working_memory: false,
    session_history: false,
  });

  // Fetch memory data for current persona
  const { data: memoryData, isLoading } = useQuery({
    queryKey: ['memory', selectedPersona?.id, sessionId],
    queryFn: () => valisApi.getMemoryData(selectedPersona!.id, sessionId),
    enabled: !!selectedPersona,
    refetchInterval: 5000, // Refresh every 5 seconds
  });

  const toggleLayer = (layer: string) => {
    setExpandedLayers(prev => ({
      ...prev,
      [layer]: !prev[layer]
    }));
  };

  if (!selectedPersona) {
    return (
      <Card className={cn("h-full", className)}>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Brain className="h-5 w-5" />
            <span>Memory Diagnostics</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center text-muted-foreground">
            <Database className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p>Select a persona to view memory layers</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (isLoading) {
    return (
      <Card className={cn("h-full", className)}>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Brain className="h-5 w-5" />
            <span>Memory Diagnostics</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center text-muted-foreground">
            <div className="animate-spin h-8 w-8 border-2 border-primary border-t-transparent rounded-full mx-auto mb-2" />
            <p>Loading memory layers...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={cn("h-full flex flex-col", className)}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Brain className="h-5 w-5" />
            <span>Memory Diagnostics</span>
          </div>
          <Badge variant="outline" className="text-xs">
            {selectedPersona.name}
          </Badge>
        </CardTitle>
      </CardHeader>
      
      <CardContent className="flex-1 space-y-3 overflow-auto">
        {/* Core Biography Layer */}
        <MemoryLayer
          title="Core Biography"
          icon={<User className="h-4 w-4" />}
          count={Object.keys(memoryData?.core_biography || {}).length}
          expanded={expandedLayers.core_biography}
          onToggle={() => toggleLayer('core_biography')}
          color="blue"
        >
          <div className="space-y-2 text-sm">
            {Object.entries(memoryData?.core_biography || {}).map(([key, value]) => (
              <div key={key} className="border-l-2 border-blue-200 pl-2">
                <div className="font-medium text-blue-900">{key}</div>
                <div className="text-muted-foreground">
                  {typeof value === 'string' ? value : JSON.stringify(value)}
                </div>
              </div>
            ))}
          </div>
        </MemoryLayer>

        {/* Canonized Identity Layer */}
        <MemoryLayer
          title="Canonized Identity"
          icon={<Star className="h-4 w-4" />}
          count={memoryData?.canonized_identity?.length || 0}
          expanded={expandedLayers.canonized_identity}
          onToggle={() => toggleLayer('canonized_identity')}
          color="yellow"
        >
          <div className="space-y-3 text-sm">
            {memoryData?.canonized_identity?.slice(-5).reverse().map((entry: any, index: number) => (
              <div key={index} className="border-l-2 border-yellow-200 pl-2">
                <div className="flex items-center justify-between mb-1">
                  <Badge variant="outline" className="text-xs">
                    Canon #{entry.canon_id || index + 1}
                  </Badge>
                  <span className="text-xs text-muted-foreground">
                    {format(new Date(entry.timestamp), 'MMM d, HH:mm')}
                  </span>
                </div>
                <div className="text-muted-foreground">
                  {entry.content.length > 100 
                    ? `${entry.content.substring(0, 100)}...` 
                    : entry.content
                  }
                </div>
              </div>
            ))}
          </div>
        </MemoryLayer>

        {/* Client Profile Layer */}
        <MemoryLayer
          title="Client Profile"
          icon={<User className="h-4 w-4" />}
          count={Object.keys(memoryData?.client_profile?.facts || {}).length}
          expanded={expandedLayers.client_profile}
          onToggle={() => toggleLayer('client_profile')}
          color="green"
        >
          <div className="space-y-2 text-sm">
            {Object.entries(memoryData?.client_profile?.facts || {}).map(([key, value]) => (
              <div key={key} className="border-l-2 border-green-200 pl-2">
                <div className="font-medium text-green-900">{key}</div>
                <div className="text-muted-foreground">{String(value)}</div>
              </div>
            ))}
          </div>
        </MemoryLayer>

        {/* Working Memory Layer */}
        <MemoryLayer
          title="Working Memory"
          icon={<Zap className="h-4 w-4" />}
          count={memoryData?.working_memory?.length || 0}
          expanded={expandedLayers.working_memory}
          onToggle={() => toggleLayer('working_memory')}
          color="purple"
        >
          <div className="space-y-2 text-sm">
            {memoryData?.working_memory?.slice(-5).reverse().map((entry: any, index: number) => (
              <div key={index} className="border-l-2 border-purple-200 pl-2">
                <div className="flex items-center justify-between mb-1">
                  <Badge variant="outline" className="text-xs">
                    {entry.type}
                  </Badge>
                  <span className="text-xs text-muted-foreground">
                    {format(new Date(entry.timestamp), 'MMM d, HH:mm')}
                  </span>
                </div>
                <div className="text-muted-foreground">{entry.content}</div>
              </div>
            ))}
          </div>
        </MemoryLayer>

        {/* Session History Layer */}
        <MemoryLayer
          title="Session History"
          icon={<MessageSquare className="h-4 w-4" />}
          count={memoryData?.session_history?.length || 0}
          expanded={expandedLayers.session_history}
          onToggle={() => toggleLayer('session_history')}
          color="gray"
        >
          <div className="space-y-2 text-sm">
            {memoryData?.session_history?.slice(-3).map((entry: any, index: number) => (
              <div key={index} className="border-l-2 border-gray-200 pl-2">
                <div className="font-medium text-gray-900 capitalize">{entry.role}</div>
                <div className="text-muted-foreground">
                  {entry.content.length > 80 
                    ? `${entry.content.substring(0, 80)}...` 
                    : entry.content
                  }
                </div>
              </div>
            ))}
          </div>
        </MemoryLayer>
      </CardContent>
    </Card>
  );
}

// Memory Layer Component
interface MemoryLayerProps {
  title: string;
  icon: React.ReactNode;
  count: number;
  expanded: boolean;
  onToggle: () => void;
  color: string;
  children: React.ReactNode;
}

function MemoryLayer({ title, icon, count, expanded, onToggle, color, children }: MemoryLayerProps) {
  const colorClasses = {
    blue: 'border-blue-200 bg-blue-50',
    yellow: 'border-yellow-200 bg-yellow-50',
    green: 'border-green-200 bg-green-50',
    purple: 'border-purple-200 bg-purple-50',
    gray: 'border-gray-200 bg-gray-50',
  };

  return (
    <Collapsible open={expanded} onOpenChange={onToggle}>
      <CollapsibleTrigger asChild>
        <Button
          variant="ghost"
          className={cn(
            "w-full justify-between p-3 h-auto border-l-4",
            colorClasses[color as keyof typeof colorClasses]
          )}
        >
          <div className="flex items-center space-x-2">
            {icon}
            <span className="font-medium">{title}</span>
            <Badge variant="secondary" className="text-xs">
              {count}
            </Badge>
          </div>
          {expanded ? (
            <ChevronDown className="h-4 w-4" />
          ) : (
            <ChevronRight className="h-4 w-4" />
          )}
        </Button>
      </CollapsibleTrigger>
      <CollapsibleContent className="px-3 pb-3">
        {count === 0 ? (
          <div className="text-sm text-muted-foreground text-center py-2">
            No {title.toLowerCase()} entries
          </div>
        ) : (
          children
        )}
      </CollapsibleContent>
    </Collapsible>
  );
}
