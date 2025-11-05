import { useState, useEffect, useCallback } from "react"
import { calculateShipping, CartItem, ShippingOption, CalculateShippingResponse } from "@client/services/shipping-api"

interface UseShippingCalculatorProps {
  cartItems: CartItem[]
  zoneId: number | null
}

interface UseShippingCalculatorReturn {
  shippingOptions: ShippingOption[]
  selectedOption: ShippingOption | null
  setSelectedOption: (option: ShippingOption | null) => void
  loading: boolean
  error: string | null
  calculate: () => Promise<void>
}

/**
 * Hook to calculate shipping costs for a cart
 */
export function useShippingCalculator({
  cartItems,
  zoneId,
}: UseShippingCalculatorProps): UseShippingCalculatorReturn {
  const [shippingOptions, setShippingOptions] = useState<ShippingOption[]>([])
  const [selectedOption, setSelectedOption] = useState<ShippingOption | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const calculate = useCallback(async () => {
    if (!zoneId || cartItems.length === 0) {
      setShippingOptions([])
      setSelectedOption(null)
      setError(null)
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response: CalculateShippingResponse = await calculateShipping(cartItems, zoneId)
      setShippingOptions(response.shipping_options)

      // Auto-select first option (usually standard/cheapest)
      if (response.shipping_options.length > 0) {
        setSelectedOption(response.shipping_options[0])
      }
    } catch (err: any) {
      console.error("Shipping calculation error:", err)
      setError(err.response?.data?.error || "Failed to calculate shipping. Please try again.")
      setShippingOptions([])
      setSelectedOption(null)
    } finally {
      setLoading(false)
    }
  }, [cartItems, zoneId])

  // Auto-calculate when cart or zone changes
  useEffect(() => {
    calculate()
  }, [calculate])

  return {
    shippingOptions,
    selectedOption,
    setSelectedOption,
    loading,
    error,
    calculate,
  }
}
