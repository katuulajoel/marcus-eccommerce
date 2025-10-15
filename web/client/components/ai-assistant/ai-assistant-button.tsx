import { MessageCircle, X } from "lucide-react"
import { useAIAssistant } from "@client/context/ai-assistant-context"
import { Button } from "@shared/components/ui/button"
import { cn } from "@shared/lib/utils"

export default function AIAssistantButton() {
  const { isOpen, togglePanel, messages } = useAIAssistant()

  const unreadCount = 0 // TODO: Implement unread message tracking

  return (
    <Button
      onClick={togglePanel}
      className={cn(
        "fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-lg transition-all duration-300 z-50",
        "bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700",
        "flex items-center justify-center",
        isOpen && "bg-gray-600 hover:bg-gray-700"
      )}
      aria-label={isOpen ? "Close AI Assistant" : "Open AI Assistant"}
    >
      {isOpen ? (
        <X className="h-6 w-6 text-white" />
      ) : (
        <>
          <MessageCircle className="h-6 w-6 text-white" />
          {unreadCount > 0 && (
            <span className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-red-500 text-white text-xs flex items-center justify-center font-bold">
              {unreadCount}
            </span>
          )}
        </>
      )}
    </Button>
  )
}
