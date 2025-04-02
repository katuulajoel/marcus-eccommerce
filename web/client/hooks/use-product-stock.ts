import { useState, useEffect } from "react"
import { fetchCategoryStock } from "@client/services/api"

interface StockInfo {
  id: number
  quantity: number
  part_option: number
}

export function useProductStock(categoryId: number | null) {
  const [stockInfo, setStockInfo] = useState<StockInfo[]>([])
  const [loading, setLoading] = useState(false)
  
  // Fetch stock information when categoryId changes
  useEffect(() => {
    if (!categoryId) return
    
    const getStockInfo = async () => {
      setLoading(true)
      try {
        const stockData = await fetchCategoryStock(categoryId)
        setStockInfo(stockData)
      } catch (err) {
        console.error("Failed to fetch stock information:", err)
        // We can still function without stock info
      } finally {
        setLoading(false)
      }
    }

    getStockInfo()
  }, [categoryId])

  // Get stock quantity for a specific option
  const getStockQuantity = (optionId: number): number => {
    const stock = stockInfo.find(item => item.part_option === optionId)
    return stock ? stock.quantity : 0
  }

  // Check if an option is in stock
  const isInStock = (optionId: number): boolean => {
    return getStockQuantity(optionId) > 0
  }

  // Get stock status text
  const getStockStatusText = (optionId: number): string => {
    const quantity = getStockQuantity(optionId)
    
    if (quantity === 0) {
      return "Out of stock"
    } else if (quantity <= 5) {
      return `Low stock (${quantity})`
    } else {
      return `In stock (${quantity})`
    }
  }

  // Check if option is low on stock
  const isLowStock = (optionId: number): boolean => {
    const quantity = getStockQuantity(optionId)
    return quantity > 0 && quantity <= 5
  }

  return {
    stockInfo,
    loading: loading,
    getStockQuantity,
    isInStock,
    isLowStock,
    getStockStatusText,
  }
}
