import { useState, useEffect } from 'react'
import { useCurrency } from '../contexts/currency-context'

interface UseConvertedPriceOptions {
  amount: number
  fromCurrency?: string
}

interface UseConvertedPriceReturn {
  convertedAmount: number
  formattedPrice: string
  isConverting: boolean
}

/**
 * Hook to convert and format prices based on selected currency
 *
 * @param amount - The amount in base currency (UGX)
 * @param fromCurrency - The source currency (defaults to 'UGX')
 * @returns Converted amount, formatted price string, and loading state
 *
 * @example
 * const { formattedPrice, isConverting } = useConvertedPrice({ amount: 100000 })
 * // Returns: "$ 27.03" when USD is selected
 */
export function useConvertedPrice({
  amount,
  fromCurrency = 'UGX'
}: UseConvertedPriceOptions): UseConvertedPriceReturn {
  const { selectedCurrency, convertAmount, formatAmount } = useCurrency()
  const [convertedAmount, setConvertedAmount] = useState(amount)
  const [isConverting, setIsConverting] = useState(false)

  useEffect(() => {
    let isMounted = true

    async function convert() {
      // Skip conversion if same currency
      if (fromCurrency === selectedCurrency) {
        setConvertedAmount(amount)
        setIsConverting(false)
        return
      }

      setIsConverting(true)

      try {
        const converted = await convertAmount(amount, fromCurrency)
        if (isMounted) {
          setConvertedAmount(converted)
        }
      } catch (error) {
        console.error('Price conversion failed:', error)
        // Fallback to original amount
        if (isMounted) {
          setConvertedAmount(amount)
        }
      } finally {
        if (isMounted) {
          setIsConverting(false)
        }
      }
    }

    convert()

    return () => {
      isMounted = false
    }
  }, [amount, fromCurrency, selectedCurrency, convertAmount])

  const formattedPrice = formatAmount(convertedAmount, selectedCurrency)

  return {
    convertedAmount,
    formattedPrice,
    isConverting,
  }
}
