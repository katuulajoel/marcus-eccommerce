import { type AIMessage } from "@client/context/ai-assistant-context"
import { cn } from "@shared/lib/utils"
import { Bot, User } from "lucide-react"
import AIProductCard from "./ai-product-card"

interface AIChatMessageProps {
  message: AIMessage
}

export default function AIChatMessage({ message }: AIChatMessageProps) {
  const isUser = message.role === "user"
  const hasProducts = message.metadata?.products && message.metadata.products.length > 0

  return (
    <div className={cn("flex gap-3 mb-4", isUser && "flex-row-reverse")}>
      {/* Avatar */}
      <div
        className={cn(
          "flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center",
          isUser
            ? "bg-gradient-to-r from-teal-500 to-blue-500"
            : "bg-gradient-to-r from-purple-600 to-pink-600"
        )}
      >
        {isUser ? (
          <User className="h-5 w-5 text-white" />
        ) : (
          <Bot className="h-5 w-5 text-white" />
        )}
      </div>

      {/* Message Content */}
      <div className={cn("flex-1 max-w-[80%]", isUser && "flex justify-end")}>
        <div className="space-y-2">
          <div
            className={cn(
              "rounded-2xl px-4 py-3 shadow-sm",
              isUser
                ? "bg-gradient-to-r from-teal-500 to-blue-500 text-white"
                : "bg-gray-100 text-gray-900"
            )}
          >
            <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>

            {/* Timestamp */}
            <p
              className={cn(
                "text-xs mt-1",
                isUser ? "text-teal-100" : "text-gray-500"
              )}
            >
              {message.timestamp.toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit"
              })}
            </p>
          </div>

          {/* Product Recommendations */}
          {!isUser && hasProducts && (
            <div className="space-y-2">
              <p className="text-xs text-gray-600 font-medium px-2">Recommended Products:</p>
              <div className="grid grid-cols-1 gap-2">
                {message.metadata.products.slice(0, 3).map((product: any) => (
                  <AIProductCard key={product.id} product={product} />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
