"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import { useAIAssistant } from "./ai-assistant-context"
import * as api from "@client/services/api"

export type CartItem = {
  id: string
  name: string
  price: number
  image: string
  quantity: number
  categoryId?: number
  configuration?: {
    frameType: string
    frameFinish: string
    wheels: string
    rimColor: string
    chain: string
  }
  configDetails?: {
    [key: string]: {
      name: string
      price: number
    }
  }
}

interface CartContextType {
  items: CartItem[]
  addItem: (item: CartItem) => Promise<void>
  removeItem: (id: string) => Promise<void>
  updateQuantity: (id: string, quantity: number) => Promise<void>
  clearCart: () => Promise<void>
  refreshCart: () => Promise<void>
  itemCount: number
  totalPrice: number
  isLoading: boolean
}

const CartContext = createContext<CartContextType | undefined>(undefined)

export function CartProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<CartItem[]>([])
  const [itemCount, setItemCount] = useState(0)
  const [totalPrice, setTotalPrice] = useState(0)
  const [isLoading, setIsLoading] = useState(false)

  const { sessionId } = useAIAssistant()

  // Fetch cart from backend when sessionId is available
  useEffect(() => {
    if (sessionId) {
      fetchCart()
    }
  }, [sessionId])

  // Calculate counts whenever items change
  useEffect(() => {
    const count = items.reduce((total, item) => total + item.quantity, 0)
    const price = items.reduce((total, item) => total + item.price * item.quantity, 0)

    setItemCount(count)
    setTotalPrice(price)
  }, [items])

  const fetchCart = async () => {
    if (!sessionId) return

    try {
      setIsLoading(true)
      const cart = await api.getCart(sessionId)

      // Transform backend cart items to CartItem format
      const transformedItems: CartItem[] = cart.items.map((item: any) => ({
        id: item.item_id,
        name: item.name,
        price: item.price,
        image: item.image_url || '/placeholder.png',
        quantity: item.quantity,
        categoryId: item.category_id,
        configuration: item.configuration,
        configDetails: item.config_details  // Map config_details to configDetails
      }))

      setItems(transformedItems)
    } catch (error) {
      console.error("Failed to fetch cart:", error)
      // On error, start with empty cart
      setItems([])
    } finally {
      setIsLoading(false)
    }
  }

  const refreshCart = async () => {
    await fetchCart()
  }

  const addItem = async (newItem: CartItem) => {
    if (!sessionId) {
      console.error("Cannot add to cart: No session ID")
      return
    }

    try {
      setIsLoading(true)

      // Extract product ID - handle both numeric IDs and timestamp-based IDs
      let productId: number
      if (typeof newItem.id === 'string' && newItem.id.includes('-')) {
        // Format: "productId-timestamp" or "custom-categoryId-timestamp"
        const parts = newItem.id.split('-')
        if (parts[0] === 'custom') {
          // For custom builds without a product, use categoryId * 10000 + timestamp hash
          // This ensures unique IDs while being parseable
          productId = (newItem.categoryId || 0) * 10000 + (Date.now() % 10000)
        } else {
          // Extract the numeric product ID
          productId = parseInt(parts[0])
        }
      } else {
        productId = parseInt(newItem.id)
      }

      // Call backend API to add item
      await api.addToCart(
        sessionId,
        productId,
        newItem.name,
        newItem.price,
        newItem.quantity,
        newItem.configuration,
        newItem.image,
        newItem.categoryId,
        newItem.configDetails
      )

      // Refresh cart from backend to get updated state
      await fetchCart()
    } catch (error) {
      console.error("Failed to add item to cart:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const removeItem = async (id: string) => {
    if (!sessionId) {
      console.error("Cannot remove from cart: No session ID")
      return
    }

    try {
      setIsLoading(true)

      // Call backend API to remove item
      await api.removeFromCart(sessionId, id)

      // Refresh cart from backend
      await fetchCart()
    } catch (error) {
      console.error("Failed to remove item from cart:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const updateQuantity = async (id: string, quantity: number) => {
    if (!sessionId) {
      console.error("Cannot update quantity: No session ID")
      return
    }

    try {
      setIsLoading(true)

      // Call backend API to update quantity
      await api.updateCartQuantity(sessionId, id, quantity)

      // Refresh cart from backend
      await fetchCart()
    } catch (error) {
      console.error("Failed to update quantity:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const clearCart = async () => {
    if (!sessionId) {
      console.error("Cannot clear cart: No session ID")
      return
    }

    try {
      setIsLoading(true)

      // Call backend API to clear cart
      await api.clearCart(sessionId)

      // Clear local state
      setItems([])
    } catch (error) {
      console.error("Failed to clear cart:", error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <CartContext.Provider
      value={{
        items,
        addItem,
        removeItem,
        updateQuantity,
        clearCart,
        refreshCart,
        itemCount,
        totalPrice,
        isLoading,
      }}
    >
      {children}
    </CartContext.Provider>
  )
}

export function useCart() {
  const context = useContext(CartContext)
  if (context === undefined) {
    throw new Error("useCart must be used within a CartProvider")
  }
  return context
}
