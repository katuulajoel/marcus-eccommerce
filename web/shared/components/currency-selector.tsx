import React from 'react'
import { useCurrency } from '../contexts/currency-context'

interface CurrencySelectorProps {
  className?: string
  variant?: 'default' | 'compact'
}

export function CurrencySelector({ className = '', variant = 'default' }: CurrencySelectorProps) {
  const { selectedCurrency, currencies, isLoading, setSelectedCurrency } = useCurrency()

  if (isLoading) {
    return (
      <div className={`animate-pulse ${className}`}>
        <div className="h-10 w-24 bg-gray-200 rounded"></div>
      </div>
    )
  }

  if (variant === 'compact') {
    return (
      <select
        value={selectedCurrency}
        onChange={(e) => setSelectedCurrency(e.target.value)}
        className={`
          px-3 py-1.5 text-sm
          border border-gray-300 rounded-md
          bg-white
          focus:outline-none focus:ring-2 focus:ring-blue-500
          ${className}
        `}
      >
        {currencies.map((currency) => (
          <option key={currency.code} value={currency.code}>
            {currency.symbol}
          </option>
        ))}
      </select>
    )
  }

  return (
    <div className={`relative ${className}`}>
      <label htmlFor="currency-select" className="block text-sm font-medium text-gray-700 mb-1">
        Currency
      </label>
      <select
        id="currency-select"
        value={selectedCurrency}
        onChange={(e) => setSelectedCurrency(e.target.value)}
        className="
          block w-full px-3 py-2
          border border-gray-300 rounded-md
          bg-white
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
          text-sm
        "
      >
        {currencies.map((currency) => (
          <option key={currency.code} value={currency.code}>
            {currency.code} - {currency.name}
          </option>
        ))}
      </select>
    </div>
  )
}
