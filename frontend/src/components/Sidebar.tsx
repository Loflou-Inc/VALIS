import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  User, 
  Users, 
  MessageCircle, 
  Clock,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { valisApi } from '@/lib/api';
import type { PersonaInfo, SessionInfo } from '@/types';

interface SidebarProps {
  personas: PersonaInfo[];
  selectedPersona: PersonaInfo | null;
  onPersonaSelect: (persona: PersonaInfo) => void;
  isLoading: boolean;
  collapsed: boolean;
}

export function Sidebar({ 
  personas, 
  selectedPersona, 
  onPersonaSelect, 
  isLoading,
  collapsed 
}: SidebarProps) {
  // Fetch active sessions
  const { data: sessions = [] } = useQuery({
    queryKey: ['sessions'],
    queryFn: valisApi.getSessions,
    refetchInterval: 10000, // Refresh every 10 seconds
  });

  if (collapsed) {
    return (
      <div className="w-16 border-r bg-muted/50 flex flex-col items-center py-4 space-y-4">
        <div className="flex flex-col space-y-2">
          {personas.slice(0, 3).map((persona) => (
            <Button
              key={persona.id}
              variant={selectedPersona?.id === persona.id ? 'default' : 'ghost'}
              size="icon"
              onClick={() => onPersonaSelect(persona)}
              title={persona.name}
            >
              <User className="h-4 w-4" />
            </Button>
          ))}
        </div>
        <div className="text-xs text-muted-foreground">
          <Users className="h-4 w-4" />
        </div>
      </div>
    );
  }

  return (
    <aside className="w-80 border-r bg-muted/50 flex flex-col">
      {/* Persona Selector Section */}
      <div className="p-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center space-x-2">
              <User className="h-5 w-5" />
              <span>AI Personas</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {isLoading ? (
              <div className="space-y-2">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="h-16 bg-muted animate-pulse rounded-md" />
                ))}
              </div>
            ) : (
              personas.map((persona) => (
                <PersonaCard
                  key={persona.id}
                  persona={persona}
                  isSelected={selectedPersona?.id === persona.id}
                  onSelect={() => onPersonaSelect(persona)}
                />
              ))
            )}
          </CardContent>
        </Card>
      </div>

      {/* Active Sessions Section */}
      <div className="p-4 flex-1">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center space-x-2">
              <MessageCircle className="h-5 w-5" />
              <span>Active Sessions</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {sessions.length === 0 ? (
              <p className="text-sm text-muted-foreground">No active sessions</p>
            ) : (
              <div className="space-y-2">
                {sessions.slice(0, 5).map((session) => (
                  <SessionCard key={session.session_id} session={session} />
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </aside>
  );
}
// PersonaCard Component
interface PersonaCardProps {
  persona: PersonaInfo;
  isSelected: boolean;
  onSelect: () => void;
}

function PersonaCard({ persona, isSelected, onSelect }: PersonaCardProps) {
  return (
    <Button
      variant={isSelected ? 'default' : 'ghost'}
      className={cn(
        "w-full justify-start h-auto p-3 text-left",
        isSelected && "ring-2 ring-ring"
      )}
      onClick={onSelect}
    >
      <div className="flex items-start space-x-3 w-full">
        <div className={cn(
          "w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium",
          isSelected 
            ? "bg-primary-foreground text-primary" 
            : "bg-muted-foreground/20 text-muted-foreground"
        )}>
          {persona.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-medium text-sm truncate">{persona.name}</h3>
          <p className="text-xs text-muted-foreground truncate">{persona.role}</p>
          {persona.description && (
            <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
              {persona.description}
            </p>
          )}
        </div>
        {persona.available && (
          <Badge variant="secondary" className="text-xs">
            Online
          </Badge>
        )}
      </div>
    </Button>
  );
}

// SessionCard Component
interface SessionCardProps {
  session: SessionInfo;
}

function SessionCard({ session }: SessionCardProps) {
  const timeAgo = React.useMemo(() => {
    const now = new Date();
    const lastActivity = new Date(session.last_activity);
    const diffMinutes = Math.floor((now.getTime() - lastActivity.getTime()) / (1000 * 60));
    
    if (diffMinutes < 1) return 'Just now';
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    const diffHours = Math.floor(diffMinutes / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  }, [session.last_activity]);

  return (
    <div className="p-2 border rounded-md bg-background/50">
      <div className="flex items-center justify-between">
        <div className="text-xs font-medium truncate">
          {session.session_id.replace('session_', '').slice(0, 8)}...
        </div>
        <Badge variant="outline" className="text-xs">
          {session.message_count || 0}
        </Badge>
      </div>
      <div className="flex items-center space-x-2 mt-1">
        <Clock className="h-3 w-3 text-muted-foreground" />
        <span className="text-xs text-muted-foreground">{timeAgo}</span>
        {session.last_persona && (
          <span className="text-xs text-muted-foreground">
            · {session.last_persona}
          </span>
        )}
      </div>
    </div>
  );
}