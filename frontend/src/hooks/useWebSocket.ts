import { useState, useEffect, useRef } from 'react'
import { toast } from 'react-hot-toast'

interface WebSocketMessage {
  type: string
  data?: any
  brand_id?: number
  message?: string
}

export const useWebSocket = (selectedBrandId: number | null) => {
  const [isConnected, setIsConnected] = useState(false)
  const [newMentions, setNewMentions] = useState<any[]>([])
  const [alerts, setAlerts] = useState<any[]>([])
  const socketRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    // Skip WebSocket connection in production for now to prevent mounting issues
    if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
      console.log('WebSocket disabled in production environment')
      return
    }

    // Connect to WebSocket
    const connectWebSocket = () => {
      try {
        const wsUrl = 'ws://localhost:8000/ws/mentions'
        const socket = new WebSocket(wsUrl)
        
        socket.onopen = () => {
          console.log('WebSocket connected')
          setIsConnected(true)
          
          // Subscribe to brand updates if brand is selected
          if (selectedBrandId) {
            socket.send(JSON.stringify({
              type: 'subscribe_brand',
              brand_id: selectedBrandId
            }))
          }
          
          // Send ping to keep connection alive
          const pingInterval = setInterval(() => {
            if (socket.readyState === WebSocket.OPEN) {
              socket.send(JSON.stringify({ type: 'ping' }))
            }
          }, 30000) // Ping every 30 seconds
          
          socket.addEventListener('close', () => {
            clearInterval(pingInterval)
          })
        }
        
        socket.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            handleWebSocketMessage(message)
          } catch (error) {
            console.error('Error parsing WebSocket message:', error)
          }
        }
        
        socket.onclose = () => {
          console.log('WebSocket disconnected')
          setIsConnected(false)
          
          // Attempt to reconnect after 3 seconds
          setTimeout(() => {
            console.log('Attempting to reconnect WebSocket...')
            connectWebSocket()
          }, 3000)
        }
        
        socket.onerror = (error) => {
          console.error('WebSocket error:', error)
          setIsConnected(false)
          // Don't attempt reconnection on error to prevent blocking
        }
        
        socketRef.current = socket
        
      } catch (error) {
        console.error('Error connecting to WebSocket:', error)
        setIsConnected(false)
        // Don't retry in production to prevent blocking React
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
          setTimeout(() => {
            connectWebSocket()
          }, 5000)
        }
      }
    }

    const handleWebSocketMessage = (message: WebSocketMessage) => {
      switch (message.type) {
        case 'new_mention':
          if (message.data) {
            setNewMentions(prev => [message.data, ...prev.slice(0, 49)]) // Keep last 50
            
            // Show toast notification for new mentions
            if (message.data.sentiment_label === 'negative') {
              toast.error(`New negative mention detected for ${message.data.brand_name || 'brand'}`)
            } else if (message.data.sentiment_label === 'positive') {
              toast.success(`New positive mention detected!`)
            } else {
              toast(`New mention detected`, {
                icon: '💬',
              })
            }
          }
          break
          
        case 'sentiment_update':
          if (message.data) {
            // Update existing mention with sentiment data
            setNewMentions(prev => 
              prev.map(mention => 
                mention.id === message.data.id 
                  ? { ...mention, ...message.data }
                  : mention
              )
            )
          }
          break
          
        case 'alert':
          if (message.data) {
            setAlerts(prev => [message.data, ...prev.slice(0, 19)]) // Keep last 20
            
            // Show alert notification
            const severity = message.data.severity
            const alertMessage = message.data.title
            
            if (severity === 'critical') {
              toast.error(`🚨 CRITICAL: ${alertMessage}`)
            } else if (severity === 'high') {
              toast.error(`⚠️ HIGH: ${alertMessage}`)
            } else if (severity === 'medium') {
              toast(`🔔 MEDIUM: ${alertMessage}`, {
                icon: '⚠️',
              })
            } else {
              toast(`ℹ️ ${alertMessage}`)
            }
          }
          break
          
        case 'subscribed':
          console.log(`Subscribed to brand ${message.brand_id} updates`)
          toast.success(`Connected to real-time updates`)
          break
          
        case 'pong':
          // Connection is alive
          break
          
        default:
          console.log('Unknown WebSocket message type:', message.type)
      }
    }

    connectWebSocket()

    // Cleanup on unmount
    return () => {
      if (socketRef.current) {
        socketRef.current.close()
      }
    }
  }, [selectedBrandId])

  // Subscribe to brand updates when brand changes
  useEffect(() => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN && selectedBrandId) {
      socketRef.current.send(JSON.stringify({
        type: 'subscribe_brand',
        brand_id: selectedBrandId
      }))
    }
  }, [selectedBrandId])

  const sendMessage = (message: any) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(message))
    }
  }

  return {
    isConnected,
    newMentions,
    alerts,
    sendMessage,
    clearMentions: () => setNewMentions([]),
    clearAlerts: () => setAlerts([])
  }
}