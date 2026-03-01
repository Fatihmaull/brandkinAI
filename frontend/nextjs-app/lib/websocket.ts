/**
 * BrandKin AI - WebSocket Client
 * Real-time status updates for Alchemy processing stages
 */

export type StageStatus = 'pending' | 'processing' | 'completed' | 'error';

export interface StageUpdate {
  stage: number;
  status: StageStatus;
  message?: string;
  progress?: number;
}

export interface WebSocketCallbacks {
  onStageUpdate?: (update: StageUpdate) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
}

export class ProjectWebSocket {
  private ws: WebSocket | null = null;
  private projectId: string;
  private callbacks: WebSocketCallbacks;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 3000;

  constructor(projectId: string, callbacks: WebSocketCallbacks) {
    this.projectId = projectId;
    this.callbacks = callbacks;
  }

  connect(): void {
    const wsUrl = `${process.env.NEXT_PUBLIC_WEBSOCKET_URL}/ws/projects/${this.projectId}`;
    
    try {
      this.ws = new WebSocket(wsUrl);
      
      this.ws.onopen = () => {
        console.log(`WebSocket connected for project ${this.projectId}`);
        this.reconnectAttempts = 0;
        this.callbacks.onConnect?.();
      };
      
      this.ws.onmessage = (event) => {
        try {
          const update: StageUpdate = JSON.parse(event.data);
          this.callbacks.onStageUpdate?.(update);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };
      
      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.callbacks.onDisconnect?.();
        this.attemptReconnect();
      };
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.callbacks.onError?.(error);
      };
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      
      setTimeout(() => {
        this.connect();
      }, this.reconnectDelay * this.reconnectAttempts);
    }
  }

  send(message: object): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }
}

export default ProjectWebSocket;
