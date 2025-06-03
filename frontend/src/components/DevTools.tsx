import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { 
  Zap, 
  Star, 
  TestTube,
  Settings
} from 'lucide-react';

interface DevToolsProps {
  onForceCanon: () => void;
  onInsertTestPrompt: () => void;
  onToggleMockMode: () => void;
  mockMode: boolean;
  lastTagsProcessed: string[];
}

export function DevTools({ 
  onForceCanon, 
  onInsertTestPrompt, 
  onToggleMockMode, 
  mockMode, 
  lastTagsProcessed 
}: DevToolsProps) {
  const [devPanelOpen, setDevPanelOpen] = useState(false);

  return (
    <Card className="p-3 bg-muted/50 border-dashed">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <Settings className="h-4 w-4" />
          <span className="text-sm font-medium">Dev Tools</span>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setDevPanelOpen(!devPanelOpen)}
        >
          {devPanelOpen ? 'Hide' : 'Show'}
        </Button>
      </div>

      {devPanelOpen && (
        <div className="space-y-3">
          {/* Memory Testing Tools */}
          <div className="flex flex-wrap gap-2">
            <Button
              size="sm"
              variant="outline"
              onClick={onForceCanon}
              className="text-xs"
            >
              <Star className="h-3 w-3 mr-1" />
              Force #canon
            </Button>
            
            <Button
              size="sm"
              variant="outline"
              onClick={onInsertTestPrompt}
              className="text-xs"
            >
              <TestTube className="h-3 w-3 mr-1" />
              Test Prompt
            </Button>
            
            <Button
              size="sm"
              variant={mockMode ? "destructive" : "outline"}
              onClick={onToggleMockMode}
              className="text-xs"
            >
              <Zap className="h-3 w-3 mr-1" />
              {mockMode ? 'Mock ON' : 'Mock OFF'}
            </Button>
          </div>

          {/* Tag Status */}
          {lastTagsProcessed.length > 0 && (
            <div className="space-y-1">
              <span className="text-xs text-muted-foreground">Last Tags:</span>
              <div className="flex flex-wrap gap-1">
                {lastTagsProcessed.map((tag, index) => (
                  <Badge key={index} variant="secondary" className="text-xs">
                    #{tag}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </Card>
  );
}
