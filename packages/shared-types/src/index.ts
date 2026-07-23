export interface SystemHealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  service: string;
  timestamp: string;
  version: string;
  components: {
    api: ComponentStatus;
    database: ComponentStatus;
    redis: ComponentStatus;
  };
}

export interface ComponentStatus {
  status: 'connected' | 'disconnected' | 'unknown';
  message?: string;
  latency_ms?: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
  };
}
