import React from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Brain, 
  Activity, 
  MessageSquare, 
  Settings, 
  Menu,
  Zap,
  Wrench
} from 'lucide-react';

interface HeaderProps {
  healthStatus: string;
  isLoading: boolean;
  viewMode: 'chat' | 'diagnostics' | 'configuration';
  onViewModeChange: (mode: 'chat' | 'diagnostics' | 'configuration') => void;
  onToggleSidebar: () => void;
}

export function Header({ 
  healthStatus, 
  isLoading, 
  viewMode, 
  onViewModeChange, 
  onToggleSidebar 
}: HeaderProps) {
  const getStatusColor = () => {
    if (isLoading) return 'secondary';
    switch (healthStatus) {
      case 'healthy': return 'default';
      case 'degraded': return 'secondary';
      case 'error': return 'destructive';
      default: return 'outline';
    }
  };

  const getStatusIcon = () => {
    if (isLoading) return <Activity className="h-3 w-3 animate-spin" />;
    switch (healthStatus) {
      case 'healthy': return <Zap className="h-3 w-3" />;
      case 'degraded': return <Activity className="h-3 w-3" />;
      case 'error': return <Activity className="h-3 w-3" />;
      default: return <Activity className="h-3 w-3" />;
    }
  };

  return (
    <header className="border-b bg-background px-4 py-3 flex items-center justify-between">
      <div className="flex items-center space-x-4">
        {/* Sidebar Toggle */}
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggleSidebar}
          className="md:hidden"
        >
          <Menu className="h-4 w-4" />
        </Button>

        {/* VALIS Logo */}
        <div className="flex items-center space-x-2">
          <Brain className="h-8 w-8 text-primary" />
          <div>
            <h1 className="text-xl font-bold">VALIS</h1>
            <p className="text-xs text-muted-foreground">
              Vast Active Living Intelligence System
            </p>
          </div>
        </div>

        {/* System Status */}
        <Badge variant={getStatusColor()} className="flex items-center space-x-1">
          {getStatusIcon()}
          <span className="capitalize">
            {isLoading ? 'Checking...' : healthStatus}
          </span>
        </Badge>
      </div>

      {/* View Mode Toggle */}
      <div className="flex items-center space-x-2">
        <Button
          variant={viewMode === 'chat' ? 'default' : 'ghost'}
          size="sm"
          onClick={() => onViewModeChange('chat')}
          className="flex items-center space-x-2"
        >
          <MessageSquare className="h-4 w-4" />
          <span className="hidden sm:inline">Chat</span>
        </Button>
        <Button
          variant={viewMode === 'diagnostics' ? 'default' : 'ghost'}
          size="sm"
          onClick={() => onViewModeChange('diagnostics')}
          className="flex items-center space-x-2"
        >
          <Settings className="h-4 w-4" />
          <span className="hidden sm:inline">Diagnostics</span>
        </Button>
        <Button
          variant={viewMode === 'configuration' ? 'default' : 'ghost'}
          size="sm"
          onClick={() => onViewModeChange('configuration')}
          className="flex items-center space-x-2"
        >
          <Wrench className="h-4 w-4" />
          <span className="hidden sm:inline">Config</span>
        </Button>
      </div>
    </header>
  );
}