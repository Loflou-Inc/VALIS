// VALIS API Type Definitions
// Doc Brown's Temporal Type Safety Requirements

export interface PersonaInfo {
  id: string;
  name: string;
  role: string;
  description?: string;
  available: boolean;
}

export interface ChatMessage {
  session_id: string;
  timestamp: number;
  persona_id: string;
  message: string;
  response: string;
  provider_used: string;
}

export interface ChatRequest {
  session_id: string;
  persona_id: string;
  message: string;
  context?: Record<string, any>;
}

export interface ChatResponse {
  success: boolean;
  response?: string;
  provider?: string;
  session_id: string;
  persona_id: string;
  timestamp: string;
  request_id?: string;
  error?: string;
  timing?: {
    processing_time: number;
    provider_time: number;
  };
}

export interface SessionInfo {
  session_id: string;
  created_at: string;
  last_activity: string;
  request_count: number;
  last_persona?: string;
  message_count?: number;
}

export interface HealthStatus {
  status: string;
  timestamp: string;
  system_info: Record<string, any>;
  providers_available: string[];
  personas_loaded: number;
  active_sessions: number;
  message_history_stats?: {
    total_messages: number;
    unique_sessions: number;
    max_per_session: number;
    cleanup_hours: number;
    max_total: number;
  };
}

export interface SystemStats {
  message_history: {
    total_messages: number;
    unique_sessions: number;
    max_per_session: number;
    cleanup_hours: number;
    max_total: number;
  };
  active_sessions: number;
  total_requests: number;
  uptime_seconds: number;
}

// UI State Types
export interface UIMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  persona_id?: string;
  provider?: string;
  loading?: boolean;
  error?: string;
}

export interface AppState {
  selectedPersona: PersonaInfo | null;
  currentSession: string | null;
  messages: UIMessage[];
  isLoading: boolean;
  error: string | null;
}