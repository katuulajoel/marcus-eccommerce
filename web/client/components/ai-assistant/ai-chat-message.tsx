import { type AIMessage } from "@client/context/ai-assistant-context"
import { cn } from "@shared/lib/utils"
import { Bot, User } from "lucide-react"
import AIProductCard from "./ai-product-card"
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

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
            {isUser ? (
              // User messages: plain text
              <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
            ) : (
              // AI messages: markdown support with custom styling
              <div className="text-sm leading-relaxed prose prose-sm max-w-none">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    // Headings
                    h1: ({node, ...props}) => <h1 className="text-lg font-bold mt-3 mb-2 first:mt-0" {...props} />,
                    h2: ({node, ...props}) => <h2 className="text-base font-bold mt-3 mb-2 first:mt-0" {...props} />,
                    h3: ({node, ...props}) => <h3 className="text-sm font-bold mt-2 mb-1 first:mt-0" {...props} />,
                    // Lists
                    ul: ({node, ...props}) => <ul className="list-disc list-inside my-2 space-y-1" {...props} />,
                    ol: ({node, ...props}) => <ol className="list-decimal list-inside my-2 space-y-1" {...props} />,
                    li: ({node, ...props}) => <li className="ml-2" {...props} />,
                    // Text formatting
                    strong: ({node, ...props}) => <strong className="font-semibold text-gray-900" {...props} />,
                    em: ({node, ...props}) => <em className="italic" {...props} />,
                    // Paragraphs
                    p: ({node, ...props}) => <p className="mb-2 last:mb-0" {...props} />,
                    // Code
                    code: ({node, inline, ...props}: any) =>
                      inline ? (
                        <code className="bg-gray-200 px-1 py-0.5 rounded text-xs font-mono" {...props} />
                      ) : (
                        <code className="block bg-gray-200 p-2 rounded text-xs font-mono my-2 overflow-x-auto" {...props} />
                      ),
                    // Links
                    a: ({node, ...props}) => <a className="text-purple-600 hover:text-purple-700 underline" {...props} />,
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              </div>
            )}

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
