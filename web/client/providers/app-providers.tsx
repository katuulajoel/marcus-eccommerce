import { type ReactNode } from "react"
import { AIAssistantProvider } from "@client/context/ai-assistant-context"
import { CartProvider } from "@client/context/cart-context"

/**
 * Provides both AI Assistant and Cart contexts
 *
 * Cart automatically syncs with backend when:
 * - AI adds items (action card triggers refreshCart)
 * - User manually adds items (cart operations call backend API)
 * - SessionId changes (cart context fetches from backend)
 */
export function AppProviders({ children }: { children: ReactNode }) {
  return (
    <AIAssistantProvider>
      <CartProvider>
        {children}
      </CartProvider>
    </AIAssistantProvider>
  )
}
