export interface AgentResponse {
  reply: string
  interaction: Record<string, any>
  conversation_id: string
  tool_called: string
}

export class AgentWebSocket {
  private ws: WebSocket | null = null
  private onMessage: (data: AgentResponse) => void
  private onError: (error: string) => void
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5

  constructor(
    onMessage: (data: AgentResponse) => void,
    onError: (error: string) => void
  ) {
    this.onMessage = onMessage
    this.onError = onError
  }

  connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const url = `${protocol}//${host}/ws/chat`

    try {
      this.ws = new WebSocket(url)

      this.ws.onopen = () => {
        this.reconnectAttempts = 0
      }

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (data.error) {
            this.onError(data.error)
          } else {
            this.onMessage(data as AgentResponse)
          }
        } catch {
          this.onError('Failed to parse server response')
        }
      }

      this.ws.onerror = () => {
        this.onError('WebSocket connection error')
      }

      this.ws.onclose = () => {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++
          setTimeout(() => this.connect(), 2000 * this.reconnectAttempts)
        }
      }
    } catch {
      this.onError('Failed to create WebSocket connection')
    }
  }

  send(message: string, conversationId: string | null) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        message,
        conversation_id: conversationId,
      }))
    } else {
      this.onError('WebSocket is not connected')
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }
}
