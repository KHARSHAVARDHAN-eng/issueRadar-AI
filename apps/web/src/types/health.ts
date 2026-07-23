export interface ComponentStatus {
  status: 'connected' | 'disconnected' | 'unknown';
  message?: string;
  latency_ms?: number;
}

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
