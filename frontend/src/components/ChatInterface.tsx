import React, { useState, useRef, useEffect } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { DevTools } from '@/components/DevTools';
import { 
  Send, 
  User, 
  Bot, 
  Clock, 
  Loader2,
  AlertCircle,
  Zap
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { valisApi } from '@/lib/api';
import type { PersonaInfo, UIMessage, ChatMessage, ChatResponseEnhanced } from '@/types';
import { format } from 'date-fns';

interface ChatInterfaceProps {
  selectedPersona: PersonaInfo | null;
  sessionId: string;
}

export function ChatInterface({ selectedPersona, sessionId }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<UIMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [forceCanon, setForceCanon] = useState(false);
  const [mockMode, setMockMode] = useState(false);
  const [lastTagsProcessed, setLastTagsProcessed] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Focus input on mount and persona change
  useEffect(() => {
    inputRef.current?.focus();
  }, [selectedPersona]);

  // Load message history when session changes
  const { data: history } = useQuery({
    queryKey: ['sessionHistory', sessionId],
    queryFn: () => valisApi.getSessionHistory(sessionId),
    enabled: !!sessionId,
  });

  // Update messages when history loads
  React.useEffect(() => {
    if (history?.messages) {
      const uiMessages: UIMessage[] = history.messages.map((msg: ChatMessage) => [
        {
          id: `${msg.timestamp}-user`,
          type: 'user' as const,
          content: msg.message,
          timestamp: new Date(msg.timestamp * 1000),
          persona_id: msg.persona_id,
        },
        {
          id: `${msg.timestamp}-assistant`,
          type: 'assistant' as const,
          content: msg.response,
          timestamp: new Date(msg.timestamp * 1000),
          persona_id: msg.persona_id,
          provider: msg.provider_used,
        }
      ]).flat();
      setMessages(uiMessages);
    }
  }, [history]);

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: valisApi.sendMessage,
    onMutate: async (variables) => {
      // Optimistic update - add user message immediately
      const userMessage: UIMessage = {
        id: `${Date.now()}-user`,
        type: 'user',
        content: variables.message,
        timestamp: new Date(),
        persona_id: variables.persona_id,
      };

      // Add loading assistant message
      const loadingMessage: UIMessage = {
        id: `${Date.now()}-loading`,
        type: 'assistant',
        content: '',
        timestamp: new Date(),
        persona_id: variables.persona_id,
        loading: true,
      };

      setMessages(prev => [...prev, userMessage, loadingMessage]);
      setInputValue('');
      
      return { userMessage, loadingMessage };
    },
    onSuccess: (response, _variables, context) => {
      // Replace loading message with actual response
      setMessages(prev => 
        prev.map(msg => 
          msg.id === context?.loadingMessage.id
            ? {
                ...msg,
                content: response.response || 'No response received',
                loading: false,
                provider: response.provider,
                error: response.success ? undefined : response.error,
              }
            : msg
        )
      );
      
      // Track memory tags from enhanced response
      const enhancedResponse = response as ChatResponseEnhanced;
      if (enhancedResponse.memory_info?.tags_processed) {
        setLastTagsProcessed(enhancedResponse.memory_info.tags_processed);
      }
    },
    onError: (error, _variables, context) => {
      // Replace loading message with error
      setMessages(prev => 
        prev.map(msg => 
          msg.id === context?.loadingMessage.id
            ? {
                ...msg,
                content: 'Failed to get response',
                loading: false,
                error: error.message,
              }
            : msg
        )
      );
    },
  });

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputValue.trim() || !selectedPersona || !sessionId) return;
    
    // Validate message length (Doc Brown's requirement)
    if (inputValue.length > 1000) {
      alert('Message too long. Please keep messages under 1000 characters.');
      return;
    }

    // Process message with dev tools
    let finalMessage = inputValue.trim();
    
    // Add #canon tag if forced
    if (forceCanon && !finalMessage.includes('#canon')) {
      finalMessage += ' #canon';
      setForceCanon(false); // Reset after use
    }

    sendMessageMutation.mutate({
      session_id: sessionId,
      persona_id: selectedPersona.id,
      message: finalMessage,
    });
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  // Dev Tools Handlers
  const handleForceCanon = () => {
    setForceCanon(true);
  };

  const handleInsertTestPrompt = () => {
    const testPrompts = [
      'I successfully resolved the team conflict using structured communication #canon',
      'The client prefers direct communication #client_fact',
      'Team shows signs of burnout - need to address workload #working_memory'
    ];
    const randomPrompt = testPrompts[Math.floor(Math.random() * testPrompts.length)];
    setInputValue(randomPrompt);
    inputRef.current?.focus();
  };

  const handleToggleMockMode = () => {
    setMockMode(!mockMode);
  };

  if (!selectedPersona) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <Bot className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-medium">Select a Persona</h3>
          <p className="text-muted-foreground">
            Choose an AI persona from the sidebar to start chatting
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-full">
      {/* Chat Header */}
      <div className="border-b px-6 py-4 bg-muted/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
              <Bot className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h2 className="font-semibold">{selectedPersona.name}</h2>
              <p className="text-sm text-muted-foreground">{selectedPersona.role}</p>
            </div>
          </div>
          <Badge variant="secondary" className="text-xs">
            Session: {sessionId.slice(-8)}
          </Badge>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-auto p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-muted-foreground">
            <MessageCircle className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p>Start a conversation with {selectedPersona.name}</p>
          </div>
        ) : (
          messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t space-y-3 p-4">
        {/* Dev Tools */}
        <DevTools
          onForceCanon={handleForceCanon}
          onInsertTestPrompt={handleInsertTestPrompt}
          onToggleMockMode={handleToggleMockMode}
          mockMode={mockMode}
          lastTagsProcessed={lastTagsProcessed}
        />
        
        <form onSubmit={handleSendMessage} className="flex space-x-2">
          <Input
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={`Message ${selectedPersona.name}...`}
            disabled={sendMessageMutation.isPending}
            className={cn(
              "flex-1",
              forceCanon && "border-yellow-500 bg-yellow-50"
            )}
            maxLength={1000}
          />
          <Button 
            type="submit" 
            disabled={!inputValue.trim() || sendMessageMutation.isPending}
            size="icon"
          >
            {sendMessageMutation.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </form>
        
        <div className="flex justify-between items-center text-xs text-muted-foreground">
          <div className="flex items-center space-x-2">
            <span>Press Enter to send, Shift+Enter for new line</span>
            {forceCanon && (
              <Badge variant="secondary" className="text-xs">
                Next: #canon
              </Badge>
            )}
          </div>
          <span>{inputValue.length}/1000</span>
        </div>
      </div>
    </div>
  );
}
// MessageBubble Component
interface MessageBubbleProps {
  message: UIMessage;
}

function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.type === 'user';

  const getProviderIcon = (provider?: string) => {
    switch (provider?.toLowerCase()) {
      case 'desktop commander mcp':
        return <Zap className="h-3 w-3" />;
      case 'openai api':
        return <Bot className="h-3 w-3" />;
      case 'anthropic api':
        return <Bot className="h-3 w-3" />;
      default:
        return <Bot className="h-3 w-3" />;
    }
  };

  return (
    <div className={cn(
      "flex space-x-3",
      isUser ? "justify-end" : "justify-start"
    )}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
          <Bot className="h-4 w-4 text-primary" />
        </div>
      )}
      
      <div className={cn(
        "max-w-[70%] space-y-1",
        isUser ? "items-end" : "items-start"
      )}>
        <Card className={cn(
          "p-3",
          isUser 
            ? "bg-primary text-primary-foreground" 
            : message.error
              ? "bg-destructive/10 border-destructive/20"
              : "bg-background"
        )}>
          {message.loading ? (
            <div className="flex items-center space-x-2">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span className="text-sm">Thinking...</span>
            </div>
          ) : message.error ? (
            <div className="flex items-center space-x-2 text-destructive">
              <AlertCircle className="h-4 w-4" />
              <span className="text-sm">{message.content || message.error}</span>
            </div>
          ) : (
            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          )}
        </Card>
        
        <div className={cn(
          "flex items-center space-x-2 text-xs text-muted-foreground",
          isUser ? "justify-end" : "justify-start"
        )}>
          <Clock className="h-3 w-3" />
          <span>{format(message.timestamp, 'HH:mm')}</span>
          
          {!isUser && message.provider && !message.loading && !message.error && (
            <>
              <span>•</span>
              <div className="flex items-center space-x-1">
                {getProviderIcon(message.provider)}
                <span>{message.provider}</span>
              </div>
            </>
          )}
        </div>
      </div>

      {isUser && (
        <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
          <User className="h-4 w-4 text-primary-foreground" />
        </div>
      )}
    </div>
  );
}

// Add missing import
import { MessageCircle } from 'lucide-react';