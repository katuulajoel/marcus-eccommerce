/**
 * Currency formatting utilities
 *
 * This module provides centralized currency formatting for the entire application.
 * The currency configuration is fetched from the backend and cached.
 */

interface CurrencyConfig {
  default_currency: string
  symbol: string
  name: string
  decimal_places: number
  thousand_separator: string
  decimal_separator: string
  display_format: string
}

// Cached currency config
let currencyConfig: CurrencyConfig | null = null

/**
 * Fetch currency configuration from the backend
 */
export async function fetchCurrencyConfig(): Promise<CurrencyConfig> {
  if (currencyConfig) {
    return currencyConfig
  }

  try {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}categories/currency-config/`)
    currencyConfig = await response.json()
    return currencyConfig!
  } catch (error) {
    console.error("Failed to fetch currency config:", error)
    // Fallback to UGX
    return {
      default_currency: "UGX",
      symbol: "UGX",
      name: "Ugandan Shilling",
      decimal_places: 0,
      thousand_separator: ",",
      decimal_separator: ".",
      display_format: "UGX {amount}",
    }
  }
}

/**
 * Format amount as currency string
 *
 * @param amount - Amount to format
 * @param options - Formatting options
 * @returns Formatted currency string
 *
 * @example
 * formatCurrency(10000) // "UGX 10,000"
 * formatCurrency(10000, { includeSymbol: false }) // "10,000"
 */
export function formatCurrency(
  amount: number,
  options: {
    includeSymbol?: boolean
    config?: CurrencyConfig
  } = {}
): string {
  const { includeSymbol = true, config = currencyConfig } = options

  if (!config) {
    // Fallback formatting if config not loaded
    return includeSymbol ? `UGX ${amount.toLocaleString()}` : amount.toLocaleString()
  }

  const { decimal_places, thousand_separator, decimal_separator, display_format, symbol } = config

  // Round to appropriate decimal places
  let formatted: string
  if (decimal_places === 0) {
    const rounded = Math.round(amount)
    formatted = rounded.toLocaleString("en-US")
  } else {
    const rounded = amount.toFixed(decimal_places)
    formatted = parseFloat(rounded).toLocaleString("en-US", {
      minimumFractionDigits: decimal_places,
      maximumFractionDigits: decimal_places,
    })
  }

  // Apply currency-specific separators
  if (thousand_separator !== ",") {
    formatted = formatted.replace(/,/g, "TEMP")
    formatted = formatted.replace(/\./g, decimal_separator)
    formatted = formatted.replace(/TEMP/g, thousand_separator)
  } else if (decimal_separator !== ".") {
    formatted = formatted.replace(/\./g, decimal_separator)
  }

  if (!includeSymbol) {
    return formatted
  }

  // Apply display format
  return display_format.replace("{amount}", formatted).replace("{symbol}", symbol)
}

/**
 * Parse currency string to number
 *
 * @param currencyString - Currency string to parse
 * @param config - Currency configuration
 * @returns Parsed number
 *
 * @example
 * parseCurrency("UGX 10,000") // 10000
 * parseCurrency("10,000") // 10000
 */
export function parseCurrency(currencyString: string, config: CurrencyConfig = currencyConfig!): number {
  if (!config) {
    // Fallback parsing
    return parseFloat(currencyString.replace(/[^0-9.-]+/g, ""))
  }

  const { thousand_separator, decimal_separator } = config

  // Remove currency symbol and spaces
  let cleaned = currencyString.replace(/[A-Z]+/g, "").trim()

  // Remove thousand separators
  cleaned = cleaned.replace(new RegExp(`\\${thousand_separator}`, "g"), "")

  // Replace decimal separator with standard dot
  if (decimal_separator !== ".") {
    cleaned = cleaned.replace(new RegExp(`\\${decimal_separator}`, "g"), ".")
  }

  return parseFloat(cleaned) || 0
}

/**
 * Get currency symbol
 */
export function getCurrencySymbol(): string {
  return currencyConfig?.symbol || "UGX"
}

/**
 * Get currency code
 */
export function getCurrencyCode(): string {
  return currencyConfig?.default_currency || "UGX"
}

/**
 * Initialize currency configuration
 * Call this when the app starts
 */
export async function initializeCurrency(): Promise<void> {
  await fetchCurrencyConfig()
}

/**
 * React hook for currency formatting
 */
export function useCurrency() {
  return {
    formatCurrency,
    parseCurrency,
    symbol: getCurrencySymbol(),
    code: getCurrencyCode(),
    config: currencyConfig,
  }
}
