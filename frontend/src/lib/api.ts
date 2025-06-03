// VALIS API Client
// Doc Brown's Temporal API Integration with Error Handling

import axios from 'axios';
import type {
  PersonaInfo,
  ChatRequest,
  ChatResponse,
  SessionInfo,
  HealthStatus,
  SystemStats,
  ChatMessage
} from '@/types';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000, // 30 second timeout
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error);
    
    if (error.code === 'ECONNABORTED') {
      throw new Error('Request timeout - please try again');
    }
    
    if (!error.response) {
      throw new Error('Network error - please check your connection');
    }
    
    const message = error.response.data?.detail || error.response.data?.error || error.message;
    throw new Error(message);
  }
);

export const valisApi = {
  // Health and system status
  async getHealth(): Promise<HealthStatus> {
    const response = await api.get<HealthStatus>('/health');
    return response.data;
  },

  async getSystemStats(): Promise<SystemStats> {
    const response = await api.get<SystemStats>('/admin/stats');
    return response.data;
  },

  // Personas
  async getPersonas(): Promise<PersonaInfo[]> {
    const response = await api.get<PersonaInfo[]>('/personas');
    return response.data;
  },

  // Sessions
  async getSessions(): Promise<SessionInfo[]> {
    const response = await api.get<SessionInfo[]>('/sessions');
    return response.data;
  },

  async getSessionHistory(sessionId: string): Promise<{ session_id: string; messages: ChatMessage[]; total_count: number }> {
    const response = await api.get(`/sessions/${sessionId}/history`);
    return response.data;
  },

  // Chat
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await api.post<ChatResponse>('/chat', request);
    return response.data;
  },

  // Configuration
  async getConfig(): Promise<any> {
    const response = await api.get('/config');
    return response.data;
  },

  async updateConfig(config: any): Promise<{ status: string; message: string }> {
    const response = await api.post('/config', config);
    return response.data;
  },

  // Memory System - Sprint 8B
  async getMemoryData(personaId: string, sessionId: string): Promise<any> {
    const response = await api.get(`/memory/${personaId}?session=${sessionId}`);
    return response.data;
  },

  async addCanonMemory(personaId: string, content: string): Promise<{ success: boolean }> {
    const response = await api.post('/memory/canon', { persona_id: personaId, content });
    return response.data;
  },

  async addClientFact(personaId: string, clientId: string, key: string, value: string): Promise<{ success: boolean }> {
    const response = await api.post('/memory/client-fact', { persona_id: personaId, client_id: clientId, key, value });
    return response.data;
  }
};