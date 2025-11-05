import { useConvertedPrice } from '../hooks/use-converted-price'

interface ConvertedPriceProps {
  amount: number
  fromCurrency?: string
  className?: string
}

export function ConvertedPrice({ amount, fromCurrency = 'UGX', className = '' }: ConvertedPriceProps) {
  const { formattedPrice, isConverting } = useConvertedPrice({ amount, fromCurrency })

  if (isConverting) {
    return <span className={className}>...</span>
  }

  return <span className={className}>{formattedPrice}</span>
}
