import React, { useState, useMemo, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Settings, 
  FileText, 
  AlertTriangle,
  CheckCircle,
  Clock,
  Layers,
  Zap,
  RefreshCw,
  Eye,
  EyeOff,
  ChevronDown,
  ChevronRight,
  Info,
  Wrench
} from 'lucide-react';
import { valisApi } from '@/lib/api';

// Doc Brown's Temporal Safeguard: Deep object comparison for config drift
const deepEqual = (obj1: any, obj2: any): boolean => {
  if (obj1 === obj2) return true;
  if (obj1 == null || obj2 == null) return false;
  if (typeof obj1 !== 'object' || typeof obj2 !== 'object') return false;
  
  const keys1 = Object.keys(obj1);
  const keys2 = Object.keys(obj2);
  
  if (keys1.length !== keys2.length) return false;
  
  for (let key of keys1) {
    if (!keys2.includes(key)) return false;
    if (!deepEqual(obj1[key], obj2[key])) return false;
  }
  
  return true;
};

// Temporal Safeguard: React.memo for config sections
const ConfigSection = React.memo(({ 
  title, 
  icon: Icon, 
  children, 
  isExpanded, 
  onToggle,
  hasChanges = false 
}: {
  title: string;
  icon: any;
  children: React.ReactNode;
  isExpanded: boolean;
  onToggle: () => void;
  hasChanges?: boolean;
}) => (
  <Card className={`transition-all ${hasChanges ? 'border-yellow-300 bg-yellow-50' : ''}`}>
    <div 
      className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50"
      onClick={onToggle}
    >
      <div className="flex items-center space-x-3">
        <Icon className="h-5 w-5" />
        <h3 className="font-medium">{title}</h3>
        {hasChanges && (
          <Badge variant="destructive" className="bg-yellow-500">
            <AlertTriangle className="h-3 w-3 mr-1" />
            Config Drift
          </Badge>
        )}
      </div>
      {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
    </div>
    {isExpanded && (
      <div className="border-t p-4">
        {children}
      </div>
    )}
  </Card>
));

const ConfigValue = React.memo(({ 
  label, 
  value, 
  type = 'string',
  hasChanged = false 
}: {
  label: string;
  value: any;
  type?: 'string' | 'number' | 'boolean' | 'array' | 'object';
  hasChanged?: boolean;
}) => {
  const formatValue = (val: any) => {
    switch (type) {
      case 'boolean':
        return val ? '✓ Enabled' : '✗ Disabled';
      case 'array':
        return Array.isArray(val) ? `[${val.length} items]` : '[]';
      case 'object':
        return typeof val === 'object' && val !== null ? 
          `{${Object.keys(val).length} properties}` : '{}';
      case 'number':
        return typeof val === 'number' ? val.toLocaleString() : String(val);
      default:
        return String(val);
    }
  };

  return (
    <div className={`flex justify-between items-center py-2 px-3 rounded ${
      hasChanged ? 'bg-yellow-100 border border-yellow-300' : 'bg-gray-50'
    }`}>
      <span className="text-sm font-medium text-gray-700">{label}</span>
      <span className={`text-sm font-mono ${
        hasChanged ? 'text-yellow-800' : 'text-gray-900'
      }`}>
        {formatValue(value)}
      </span>
    </div>
  );
});

const ProviderCascadeVisualizer = React.memo(({ providers }: { providers: string[] }) => (
  <div className="space-y-2">
    <p className="text-sm text-gray-600 mb-3">Provider cascade order (top priority first):</p>
    {providers.map((provider, index) => (
      <div 
        key={provider}
        className="flex items-center space-x-3 p-3 bg-blue-50 border border-blue-200 rounded"
      >
        <div className="flex items-center justify-center w-6 h-6 bg-blue-500 text-white text-xs font-bold rounded-full">
          {index + 1}
        </div>
        <span className="font-medium">{provider}</span>
        {index < providers.length - 1 && (
          <div className="flex-1 text-right text-gray-400">
            <ChevronRight className="h-4 w-4 inline" />
          </div>
        )}
      </div>
    ))}
  </div>
));

export const ConfigurationViewer: React.FC = () => {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['providers']));
  const [showSensitive, setShowSensitive] = useState(false);
  const [previousConfig, setPreviousConfig] = useState<any>(null);

  // Doc Brown's requirement: Detect config drift
  const configQuery = useQuery({
    queryKey: ['config'],
    queryFn: () => valisApi.getConfig(),
    refetchInterval: 30000, // Check every 30 seconds
    staleTime: 10000,
    onSuccess: (newConfig) => {
      if (previousConfig && !deepEqual(previousConfig, newConfig)) {
        // Config drift detected!
        console.log('🚨 CONFIG DRIFT DETECTED!', { previous: previousConfig, current: newConfig });
      }
      setPreviousConfig(newConfig);
    }
  });

  const toggleSection = (section: string) => {
    setExpandedSections(prev => {
      const newSet = new Set(prev);
      if (newSet.has(section)) {
        newSet.delete(section);
      } else {
        newSet.add(section);
      }
      return newSet;
    });
  };

  // Temporal Safeguard: Memoized config analysis
  const configAnalysis = useMemo(() => {
    const config = configQuery.data;
    if (!config) return null;

    const hasConfigDrift = previousConfig && !deepEqual(previousConfig, config);

    return {
      hasConfigDrift,
      totalProviders: config.providers?.length || 0,
      timeoutLimits: {
        provider: config.provider_timeout || 30,
        circuit_breaker: config.circuit_breaker_timeout || 300,
        request: config.max_concurrent_requests || 10
      },
      memoryEnabled: config.neural_memory?.enabled || false,
      features: {
        circuit_breaker: config.features?.enable_circuit_breaker || false,
        retry_logic: config.features?.enable_retry_logic || false,
        neural_memory: config.neural_memory?.enabled || false
      }
    };
  }, [configQuery.data, previousConfig]);

  // Cleanup effect
  useEffect(() => {
    return () => {
      configQuery.remove?.();
    };
  }, []);

  if (configQuery.isLoading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <Settings className="h-8 w-8 animate-spin mx-auto mb-2" />
            <p>Loading configuration...</p>
          </div>
        </div>
      </div>
    );
  }

  if (configQuery.isError || !configQuery.data) {
    return (
      <div className="p-6">
        <Card className="p-6 text-center">
          <AlertTriangle className="h-12 w-12 mx-auto mb-4 text-red-500" />
          <h3 className="text-lg font-semibold mb-2">Configuration Unavailable</h3>
          <p className="text-gray-600 mb-4">Unable to load system configuration.</p>
          <Button onClick={() => configQuery.refetch()}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </Card>
      </div>
    );
  }

  const config = configQuery.data;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Configuration Viewer</h2>
          <p className="text-gray-600">Current VALIS system configuration</p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowSensitive(!showSensitive)}
          >
            {showSensitive ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            {showSensitive ? 'Hide' : 'Show'} Sensitive
          </Button>
          
          <Button
            variant="outline"
            size="sm"
            onClick={() => configQuery.refetch()}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Config Drift Alert */}
      {configAnalysis?.hasConfigDrift && (
        <Card className="border-red-300 bg-red-50">
          <div className="p-4">
            <div className="flex items-center space-x-3">
              <AlertTriangle className="h-6 w-6 text-red-600" />
              <div>
                <h3 className="font-semibold text-red-800">Configuration Drift Detected!</h3>
                <p className="text-red-700 text-sm">
                  Running configuration differs from previous state. System behavior may have changed.
                </p>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Configuration Sections */}
      <div className="space-y-4">
        
        {/* Provider Cascade */}
        <ConfigSection
          title="Provider Cascade"
          icon={Layers}
          isExpanded={expandedSections.has('providers')}
          onToggle={() => toggleSection('providers')}
          hasChanges={configAnalysis?.hasConfigDrift}
        >
          <div className="space-y-4">
            <ProviderCascadeVisualizer providers={config.providers || []} />
            <div className="grid grid-cols-2 gap-4">
              <ConfigValue 
                label="Total Providers" 
                value={config.providers?.length || 0}
                type="number"
              />
              <ConfigValue 
                label="Fallback Enabled" 
                value={config.providers?.includes('hardcoded_fallback') || false}
                type="boolean"
              />
            </div>
          </div>
        </ConfigSection>

        {/* Timeout Limits */}
        <ConfigSection
          title="Timeout Configuration"
          icon={Clock}
          isExpanded={expandedSections.has('timeouts')}
          onToggle={() => toggleSection('timeouts')}
        >
          <div className="space-y-2">
            <ConfigValue 
              label="Provider Timeout" 
              value={`${config.provider_timeout || 30}s`}
              type="string"
            />
            <ConfigValue 
              label="Circuit Breaker Timeout" 
              value={`${config.circuit_breaker_timeout || 300}s`}
              type="string"
            />
            <ConfigValue 
              label="Max Concurrent Requests" 
              value={config.max_concurrent_requests || 10}
              type="number"
            />
            {config.retry_schedule && (
              <ConfigValue 
                label="Retry Schedule" 
                value={config.retry_schedule}
                type="array"
              />
            )}
          </div>
        </ConfigSection>

        {/* Feature Flags */}
        <ConfigSection
          title="Feature Flags"
          icon={Zap}
          isExpanded={expandedSections.has('features')}
          onToggle={() => toggleSection('features')}
        >
          <div className="space-y-2">
            <ConfigValue 
              label="Circuit Breaker" 
              value={config.features?.enable_circuit_breaker || false}
              type="boolean"
            />
            <ConfigValue 
              label="Retry Logic" 
              value={config.features?.enable_retry_logic || false}
              type="boolean"
            />
            <ConfigValue 
              label="Neural Memory" 
              value={config.neural_memory?.enabled || false}
              type="boolean"
            />
            {config.neural_memory?.enabled && (
              <>
                <ConfigValue 
                  label="Memory Store Type" 
                  value={config.neural_memory?.store_type || 'flat_file'}
                  type="string"
                />
                <ConfigValue 
                  label="Max Memory Size" 
                  value={config.neural_memory?.max_memories || 1000}
                  type="number"
                />
              </>
            )}
          </div>
        </ConfigSection>

        {/* System Settings */}
        <ConfigSection
          title="System Settings"
          icon={Wrench}
          isExpanded={expandedSections.has('system')}
          onToggle={() => toggleSection('system')}
        >
          <div className="space-y-2">
            <ConfigValue 
              label="Default Shell" 
              value={config.defaultShell || 'powershell'}
              type="string"
            />
            <ConfigValue 
              label="Telemetry Enabled" 
              value={config.telemetryEnabled || false}
              type="boolean"
            />
            <ConfigValue 
              label="File Read Line Limit" 
              value={config.fileReadLineLimit || 1000}
              type="number"
            />
            <ConfigValue 
              label="File Write Line Limit" 
              value={config.fileWriteLineLimit || 50}
              type="number"
            />
            {showSensitive && config.blockedCommands && (
              <ConfigValue 
                label="Blocked Commands" 
                value={config.blockedCommands}
                type="array"
              />
            )}
          </div>
        </ConfigSection>

      </div>

      {/* Footer */}
      <div className="flex items-center justify-between text-sm text-gray-500 pt-4 border-t">
        <div className="flex items-center space-x-4">
          <div className="flex items-center">
            <CheckCircle className="h-3 w-3 text-green-500 mr-1" />
            Configuration Valid
          </div>
          <div className="flex items-center">
            <Info className="h-3 w-3 mr-1" />
            Auto-refresh: 30s
          </div>
        </div>
        <div className="text-xs">
          Last updated: {new Date().toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
};