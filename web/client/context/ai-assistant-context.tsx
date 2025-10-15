"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"

export type AIMessage = {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
  metadata?: {
    products?: Array<{
      id: number
      name: string
      category: string
      category_id?: number
      base_price: number
      description: string
      image_url?: string
    }>
    configurationSuggestion?: { [key: string]: string }
    actionType?: "recommend" | "configure" | "info"
  }
}

export type AISessionContext = {
  currentPage?: string
  categoryId?: number | null
  productId?: string | null
  configuration?: { [key: string]: string }
  cartItems?: any[]
}

interface AIAssistantContextType {
  isOpen: boolean
  messages: AIMessage[]
  isLoading: boolean
  sessionContext: AISessionContext
  sessionId: string | null
  openPanel: () => void
  closePanel: () => void
  togglePanel: () => void
  sendMessage: (content: string) => Promise<void>
  updateSessionContext: (context: Partial<AISessionContext>) => void
  clearMessages: () => void
}

const AIAssistantContext = createContext<AIAssistantContextType | undefined>(undefined)

export function AIAssistantProvider({ children }: { children: ReactNode }) {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<AIMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [sessionContext, setSessionContext] = useState<AISessionContext>({})
  const [sessionId, setSessionId] = useState<string | null>(null)

  // Generate or retrieve session ID from localStorage
  useEffect(() => {
    const storedSessionId = localStorage.getItem("ai-session-id")
    if (storedSessionId) {
      setSessionId(storedSessionId)
    } else {
      const newSessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      localStorage.setItem("ai-session-id", newSessionId)
      setSessionId(newSessionId)
    }

    // Load previous messages from localStorage
    const storedMessages = localStorage.getItem("ai-messages")
    if (storedMessages) {
      try {
        const parsedMessages = JSON.parse(storedMessages)
        // Convert timestamp strings back to Date objects
        const messagesWithDates = parsedMessages.map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp)
        }))
        setMessages(messagesWithDates)
      } catch (error) {
        console.error("Failed to parse stored messages:", error)
      }
    }
  }, [])

  // Save messages to localStorage whenever they change
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem("ai-messages", JSON.stringify(messages))
    }
  }, [messages])

  const openPanel = () => setIsOpen(true)
  const closePanel = () => setIsOpen(false)
  const togglePanel = () => setIsOpen(prev => !prev)

  const sendMessage = async (content: string) => {
    if (!content.trim() || !sessionId) return

    // Add user message immediately
    const userMessage: AIMessage = {
      id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      role: "user",
      content: content.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    try {
      // Import API function dynamically to avoid circular dependencies
      const { sendAIChatMessage } = await import("@client/services/api")

      // Send message to backend
      const response = await sendAIChatMessage(sessionId, content.trim(), sessionContext)

      // Add AI response to messages
      const aiMessage: AIMessage = {
        id: response.message_id.toString(),
        role: response.role,
        content: response.content,
        timestamp: new Date(response.timestamp),
        metadata: response.metadata
      }

      setMessages(prev => [...prev, aiMessage])
    } catch (error) {
      console.error("Failed to send message:", error)

      // Add error message
      const errorMessage: AIMessage = {
        id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        role: "assistant",
        content: "I'm sorry, I encountered an error. Please try again.",
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const updateSessionContext = (context: Partial<AISessionContext>) => {
    setSessionContext(prev => ({
      ...prev,
      ...context
    }))
  }

  const clearMessages = () => {
    setMessages([])
    localStorage.removeItem("ai-messages")
  }

  return (
    <AIAssistantContext.Provider
      value={{
        isOpen,
        messages,
        isLoading,
        sessionContext,
        sessionId,
        openPanel,
        closePanel,
        togglePanel,
        sendMessage,
        updateSessionContext,
        clearMessages
      }}
    >
      {children}
    </AIAssistantContext.Provider>
  )
}

export function useAIAssistant() {
  const context = useContext(AIAssistantContext)
  if (context === undefined) {
    throw new Error("useAIAssistant must be used within an AIAssistantProvider")
  }
  return context
}
