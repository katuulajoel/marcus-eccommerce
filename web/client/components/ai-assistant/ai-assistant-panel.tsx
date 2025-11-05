import { useState, useRef, useEffect } from "react"
import { Send, Trash2, Sparkles } from "lucide-react"
import { useAIAssistant } from "@client/context/ai-assistant-context"
import { Button } from "@shared/components/ui/button"
import { Input } from "@shared/components/ui/input"
import { ScrollArea } from "@shared/components/ui/scroll-area"
import { cn } from "@shared/lib/utils"
import AIChatMessage from "./ai-chat-message"

const QUICK_ACTIONS = [
  "Show me explosion boxes",
  "Birthday gift ideas",
  "What's affordable?",
  "Help me personalize"
]

export default function AIAssistantPanel() {
  const { isOpen, messages, isLoading, sendMessage, clearMessages } = useAIAssistant()
  const [inputValue, setInputValue] = useState("")
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector("[data-radix-scroll-area-viewport]")
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight
      }
    }
  }, [messages])

  // Focus input when panel opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isOpen])

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return

    await sendMessage(inputValue)
    setInputValue("")
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleQuickAction = (action: string) => {
    sendMessage(action)
  }

  if (!isOpen) return null

  return (
    <div
      role="complementary"
      aria-label="AI Shopping Assistant"
      className={cn(
        "fixed bottom-24 right-4 md:right-6 w-[calc(100vw-2rem)] md:w-96 h-[600px] max-h-[80vh] bg-white rounded-2xl shadow-2xl z-50",
        "flex flex-col border border-gray-200 overflow-hidden",
        "transition-all duration-300 ease-in-out",
        "animate-in slide-in-from-bottom-4 fade-in"
      )}
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5" />
          <div>
            <h3 className="font-semibold text-base">AI Assistant</h3>
            <p className="text-xs text-purple-100">Here to help you customize</p>
          </div>
        </div>
        {messages.length > 0 && (
          <Button
            variant="ghost"
            size="sm"
            onClick={clearMessages}
            className="text-white hover:bg-purple-700 h-8 w-8 p-0"
            title="Clear conversation"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        )}
      </div>

      {/* Messages Area */}
      <ScrollArea ref={scrollAreaRef} className="flex-1 p-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center px-4">
            <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-full h-16 w-16 flex items-center justify-center mb-4">
              <Sparkles className="h-8 w-8 text-white" />
            </div>
            <h4 className="font-semibold text-lg mb-2">Welcome to AI Assistant!</h4>
            <p className="text-sm text-gray-600 mb-6">
              I can help you find the perfect gift, customize your order, and answer your questions.
            </p>

            {/* Quick Actions */}
            <div className="w-full space-y-2">
              <p className="text-xs text-gray-500 font-medium mb-3">Try asking:</p>
              {QUICK_ACTIONS.map((action, index) => (
                <button
                  key={index}
                  onClick={() => handleQuickAction(action)}
                  className="w-full text-left px-4 py-2 text-sm bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors border border-gray-200"
                >
                  {action}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div>
            {messages.map((message) => (
              <AIChatMessage key={message.id} message={message} />
            ))}
            {isLoading && (
              <div className="flex gap-3 mb-4">
                <div className="flex-shrink-0 h-8 w-8 rounded-full bg-gradient-to-r from-purple-600 to-pink-600 flex items-center justify-center">
                  <Sparkles className="h-5 w-5 text-white animate-pulse" />
                </div>
                <div className="flex-1">
                  <div className="bg-gray-100 rounded-2xl px-4 py-3 shadow-sm">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </ScrollArea>

      {/* Input Area */}
      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <div className="flex gap-2">
          <Input
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything..."
            disabled={isLoading}
            className="flex-1"
          />
          <Button
            onClick={handleSend}
            disabled={!inputValue.trim() || isLoading}
            className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
            size="icon"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          AI can make mistakes. Verify important information.
        </p>
      </div>
    </div>
  )
}
