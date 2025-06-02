import React, { useState, useEffect, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Activity, 
  Users, 
  Zap, 
  Clock, 
  Server, 
  AlertTriangle,
  CheckCircle,
  XCircle,
  BarChart3,
  Settings,
  RefreshCw,
  WifiOff
} from 'lucide-react';
import { valisApi } from '@/lib/api';
import type { HealthResponse, SessionInfo } from '@/types';

// Doc Brown's Temporal Safeguards: Exponential backoff for failed requests
const usePollingQuery = (queryKey: string[], queryFn: () => Promise<any>, intervalMs: number) => {
  const [retryCount, setRetryCount] = useState(0);
  const [isOnline, setIsOnline] = useState(true);

  // Calculate backoff delay: 15s, 30s, 60s, 120s max
  const backoffDelay = Math.min(intervalMs * Math.pow(2, retryCount), 120000);

  const query = useQuery({
    queryKey,
    queryFn,
    refetchInterval: isOnline ? backoffDelay : false,
    staleTime: 5000, // Doc Brown's requirement: proper caching
    gcTime: 30000,
    retry: false, // Handle retries manually with backoff
    onSuccess: () => {
      setRetryCount(0); // Reset on success
      setIsOnline(true);
    },
    onError: () => {
      setRetryCount(prev => prev + 1);
      if (retryCount >= 3) {
        setIsOnline(false); // Stop polling after multiple failures
      }
    }
  });

  // Manual retry function
  const manualRetry = () => {
    setRetryCount(0);
    setIsOnline(true);
    query.refetch();
  };

  return { ...query, isOnline, manualRetry, backoffDelay };
};

// Temporal Safeguard: React.memo to prevent unnecessary re-renders
const MetricCard = React.memo(({ 
  title, 
  value, 
  icon: Icon, 
  status = 'neutral',
  subtitle,
  onClick 
}: {
  title: string;
  value: string | number;
  icon: any;
  status?: 'success' | 'warning' | 'error' | 'neutral';
  subtitle?: string;
  onClick?: () => void;
}) => {
  const statusColors = {
    success: 'text-green-600 border-green-200 bg-green-50',
    warning: 'text-yellow-600 border-yellow-200 bg-yellow-50', 
    error: 'text-red-600 border-red-200 bg-red-50',
    neutral: 'text-blue-600 border-blue-200 bg-blue-50'
  };

  return (
    <Card 
      className={`p-4 cursor-pointer transition-all hover:shadow-md ${statusColors[status]}`}
      onClick={onClick}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold">{value}</p>
          {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
        </div>
        <Icon className="h-8 w-8" />
      </div>
    </Card>
  );
});

const ProviderStatusCard = React.memo(({ 
  name, 
  status, 
  requestCount = 0,
  failureCount = 0,
  lastUsed 
}: {
  name: string;
  status: 'available' | 'unavailable' | 'circuit_open';
  requestCount?: number;
  failureCount?: number;
  lastUsed?: string;
}) => {
  const statusConfig = {
    available: { color: 'success', icon: CheckCircle, label: 'Online' },
    unavailable: { color: 'error', icon: XCircle, label: 'Offline' },
    circuit_open: { color: 'warning', icon: AlertTriangle, label: 'Circuit Open' }
  } as const;

  const config = statusConfig[status];

  return (
    <Card className="p-3">
      <div className="flex items-center justify-between mb-2">
        <h4 className="font-medium">{name}</h4>
        <Badge variant={config.color === 'success' ? 'default' : 'destructive'}>
          <config.icon className="h-3 w-3 mr-1" />
          {config.label}
        </Badge>
      </div>
      <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
        <div>Requests: {requestCount}</div>
        <div>Failures: {failureCount}</div>
        {lastUsed && (
          <div className="col-span-2 text-xs">
            Last used: {new Date(lastUsed).toLocaleTimeString()}
          </div>
        )}
      </div>
    </Card>
  );
});

export const SystemDiagnostics: React.FC = () => {
  const [selectedView, setSelectedView] = useState<'overview' | 'sessions' | 'providers'>('overview');

  // Doc Brown's Temporal Safeguard: Polling with exponential backoff
  const healthQuery = usePollingQuery(
    ['health'],
    () => valisApi.getHealth(),
    15000 // 15 second base interval
  );

  const sessionsQuery = usePollingQuery(
    ['sessions'],
    () => valisApi.getSessions(),
    15000
  );

  // Derived state with memoization to prevent recalculation
  const diagnostics = useMemo(() => {
    const health = healthQuery.data;
    const sessions = sessionsQuery.data;

    if (!health || !sessions) return null;

    const activeSessions = sessions.filter((s: SessionInfo) => {
      const lastActivity = new Date(s.last_activity);
      const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000);
      return lastActivity > fiveMinutesAgo;
    });

    return {
      systemStatus: health.status,
      totalProviders: health.providers_available?.length || 0,
      activeProviders: health.providers_available?.filter((p: any) => p.status === 'available').length || 0,
      activeSessions: activeSessions.length,
      totalSessions: sessions.length,
      totalRequests: health.total_requests || 0,
      memoryEnabled: health.neural_memory_enabled || false,
      providers: health.providers_available || [],
      sessions: sessions
    };
  }, [healthQuery.data, sessionsQuery.data]);

  // Temporal Safeguard: Cleanup intervals on unmount
  useEffect(() => {
    return () => {
      // React Query handles cleanup automatically, but we ensure it here
      healthQuery.remove?.();
      sessionsQuery.remove?.();
    };
  }, []);

  if (healthQuery.isLoading || sessionsQuery.isLoading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <Activity className="h-8 w-8 animate-spin mx-auto mb-2" />
            <p>Loading system diagnostics...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!healthQuery.isOnline) {
    return (
      <div className="p-6">
        <Card className="p-6 text-center">
          <WifiOff className="h-12 w-12 mx-auto mb-4 text-red-500" />
          <h3 className="text-lg font-semibold mb-2">Connection Lost</h3>
          <p className="text-gray-600 mb-4">
            Unable to connect to VALIS backend. Retrying in {Math.round(healthQuery.backoffDelay / 1000)}s...
          </p>
          <Button onClick={healthQuery.manualRetry}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry Now
          </Button>
        </Card>
      </div>
    );
  }

  if (!diagnostics) {
    return (
      <div className="p-6">
        <Card className="p-6 text-center">
          <AlertTriangle className="h-12 w-12 mx-auto mb-4 text-yellow-500" />
          <h3 className="text-lg font-semibold mb-2">Diagnostics Unavailable</h3>
          <p className="text-gray-600">Unable to load system diagnostics data.</p>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">System Diagnostics</h2>
          <p className="text-gray-600">Real-time VALIS system monitoring</p>
        </div>
        
        {/* View Toggle */}
        <div className="flex bg-gray-100 rounded-lg p-1">
          {(['overview', 'sessions', 'providers'] as const).map((view) => (
            <Button
              key={view}
              variant={selectedView === view ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setSelectedView(view)}
              className="capitalize"
            >
              {view}
            </Button>
          ))}
        </div>
      </div>

      {/* Overview Metrics */}
      {selectedView === 'overview' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            title="System Status"
            value={diagnostics.systemStatus}
            icon={diagnostics.systemStatus === 'healthy' ? CheckCircle : AlertTriangle}
            status={diagnostics.systemStatus === 'healthy' ? 'success' : 'warning'}
          />
          
          <MetricCard
            title="Active Sessions" 
            value={diagnostics.activeSessions}
            icon={Users}
            subtitle={`${diagnostics.totalSessions} total`}
            status="neutral"
          />
          
          <MetricCard
            title="Providers Online"
            value={`${diagnostics.activeProviders}/${diagnostics.totalProviders}`}
            icon={Server}
            status={diagnostics.activeProviders === diagnostics.totalProviders ? 'success' : 'warning'}
          />
          
          <MetricCard
            title="Total Requests"
            value={diagnostics.totalRequests.toLocaleString()}
            icon={BarChart3}
            subtitle="All time"
            status="neutral"
          />
        </div>
      )}

      {/* Provider Status View */}
      {selectedView === 'providers' && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Provider Status</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {diagnostics.providers.map((provider: any, index: number) => (
              <ProviderStatusCard
                key={index}
                name={provider.name || `Provider ${index + 1}`}
                status={provider.status || 'unavailable'}
                requestCount={provider.request_count || 0}
                failureCount={provider.failure_count || 0}
                lastUsed={provider.last_used}
              />
            ))}
          </div>
        </div>
      )}

      {/* Sessions View */}
      {selectedView === 'sessions' && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Active Sessions</h3>
          <div className="space-y-2">
            {diagnostics.sessions.length > 0 ? (
              diagnostics.sessions.map((session: SessionInfo) => (
                <Card key={session.session_id} className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Session: {session.session_id}</p>
                      <p className="text-sm text-gray-600">
                        {session.message_count || 0} messages • Last active: {new Date(session.last_activity).toLocaleString()}
                      </p>
                    </div>
                    <Badge variant="outline">
                      <Clock className="h-3 w-3 mr-1" />
                      Active
                    </Badge>
                  </div>
                </Card>
              ))
            ) : (
              <Card className="p-6 text-center">
                <Users className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                <p className="text-gray-600">No active sessions</p>
              </Card>
            )}
          </div>
        </div>
      )}

      {/* Footer Status */}
      <div className="flex items-center justify-between text-sm text-gray-500 pt-4 border-t">
        <div className="flex items-center space-x-4">
          <div className="flex items-center">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
            Neural Memory: {diagnostics.memoryEnabled ? 'Enabled' : 'Disabled'}
          </div>
          <div className="flex items-center">
            <Activity className="h-3 w-3 mr-1" />
            Last updated: {new Date().toLocaleTimeString()}
          </div>
        </div>
        
        <Button variant="ghost" size="sm" onClick={() => {
          healthQuery.refetch();
          sessionsQuery.refetch();
        }}>
          <RefreshCw className="h-3 w-3 mr-1" />
          Refresh
        </Button>
      </div>
    </div>
  );
};