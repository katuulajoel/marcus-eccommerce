import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'

export interface Currency {
  code: string
  name: string
  symbol: string
  decimal_places: number
}

interface CurrencyContextType {
  selectedCurrency: string
  currencies: Currency[]
  isLoading: boolean
  setSelectedCurrency: (code: string) => void
  convertAmount: (amount: number, fromCurrency?: string) => Promise<number>
  formatAmount: (amount: number, currencyCode?: string) => string
  getCurrencyInfo: (code: string) => Currency | undefined
}

const CurrencyContext = createContext<CurrencyContextType | undefined>(undefined)

// Ensure API_BASE_URL has trailing slash
const getApiBaseUrl = () => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  return baseUrl.endsWith('/') ? baseUrl : `${baseUrl}/`
}
const API_BASE_URL = getApiBaseUrl()

interface CurrencyProviderProps {
  children: ReactNode
}

export function CurrencyProvider({ children }: CurrencyProviderProps) {
  const [selectedCurrency, setSelectedCurrencyState] = useState<string>('UGX')
  const [currencies, setCurrencies] = useState<Currency[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // Load currencies from API on mount
  useEffect(() => {
    loadCurrencies()
    loadSavedCurrency()
  }, [])

  async function loadCurrencies() {
    try {
      const response = await fetch(`${API_BASE_URL}api/currency/all/`)
      const data = await response.json()
      setCurrencies(data)
    } catch (error) {
      console.error('Failed to load currencies:', error)
      // Fallback to UGX only
      setCurrencies([
        { code: 'UGX', name: 'Ugandan Shilling', symbol: 'UGX', decimal_places: 0 }
      ])
    } finally {
      setIsLoading(false)
    }
  }

  function loadSavedCurrency() {
    const saved = localStorage.getItem('selectedCurrency')
    if (saved) {
      setSelectedCurrencyState(saved)
    }
  }

  function setSelectedCurrency(code: string) {
    setSelectedCurrencyState(code)
    localStorage.setItem('selectedCurrency', code)
  }

  async function convertAmount(amount: number, fromCurrency: string = 'UGX'): Promise<number> {
    // No conversion needed if same currency
    if (fromCurrency === selectedCurrency) {
      return amount
    }

    try {
      const response = await fetch(`${API_BASE_URL}api/currency/convert/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          amount,
          from_currency: fromCurrency,
          to_currency: selectedCurrency,
        }),
      })

      const data = await response.json()
      return data.converted_amount
    } catch (error) {
      console.error('Currency conversion failed:', error)
      return amount
    }
  }

  function formatAmount(amount: number, currencyCode?: string): string {
    const code = currencyCode || selectedCurrency
    const currency = currencies.find(c => c.code === code)

    if (!currency) {
      return `${code} ${amount.toLocaleString()}`
    }

    const formatted = currency.decimal_places === 0
      ? Math.round(amount).toLocaleString()
      : amount.toFixed(currency.decimal_places)

    return `${currency.symbol} ${formatted}`
  }

  function getCurrencyInfo(code: string): Currency | undefined {
    return currencies.find(c => c.code === code)
  }

  return (
    <CurrencyContext.Provider
      value={{
        selectedCurrency,
        currencies,
        isLoading,
        setSelectedCurrency,
        convertAmount,
        formatAmount,
        getCurrencyInfo,
      }}
    >
      {children}
    </CurrencyContext.Provider>
  )
}

export function useCurrency() {
  const context = useContext(CurrencyContext)
  if (context === undefined) {
    throw new Error('useCurrency must be used within a CurrencyProvider')
  }
  return context
}
