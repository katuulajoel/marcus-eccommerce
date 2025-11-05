import { ShoppingCart, Loader2 } from "lucide-react"
import { Badge } from "@shared/components/ui/badge"
import { Button } from "@shared/components/ui/button"
import { useConvertedPrice } from "@shared/hooks/use-converted-price"

interface ConfigSummaryProps {
  configuration: { [key: string]: string }
  parts: any[]
  configDetails: { [key: string]: { name: string; price: number } }
  totalPrice: number
  isConfigurationComplete: boolean
  productName?: string
  onAddToCart: () => void
  currentImage: string
}

export function ConfigSummary({
  configuration,
  parts,
  configDetails,
  totalPrice,
  isConfigurationComplete,
  productName,
  onAddToCart,
  currentImage
}: ConfigSummaryProps) {
  return (
    <div className="space-y-4">
      <div className="bg-gray-50 p-4 rounded-lg mb-6">
        <div className="relative w-full h-[300px] mx-auto">
          <img
            src={currentImage}
            alt="Product Preview"
            className="object-contain w-full h-full"
          />
        </div>
      </div>

      <h3 className="text-xl font-semibold">Configuration Summary</h3>
      
      <div className="flex flex-wrap gap-2 mb-4">
        {Object.entries(configuration).map(([partName, optionId]) => {
          const part = parts.find((p) => p.name === partName)
          if (!part) return null
          
          const option = part.options.find((opt) => opt.id.toString() === optionId)
          if (!option) return null

          return (
            <Badge key={partName} variant="outline" className="bg-white">
              {option.name}
            </Badge>
          )
        })}
      </div>
      
      <ul className="space-y-3">
        {Object.entries(configDetails).map(([partName, details]) => (
          <li key={partName} className="flex justify-between items-center py-2 border-b">
            <span className="text-gray-600">{partName}</span>
            <div className="flex items-center">
              <span className="font-medium mr-4">{details.name}</span>
              <span className="text-teal-600 font-semibold">
                {details.price > 0 ? (
                  <PriceDisplay amount={details.price} />
                ) : (
                  "Included"
                )}
              </span>
            </div>
          </li>
        ))}

        {/* Show unconfigured parts as pending */}
        {parts.filter((part) => !configuration[part.name]).map((part) => (
          <li key={part.name} className="flex justify-between items-center py-2 border-b">
            <span className="text-gray-600">{part.name}</span>
            <span className="text-amber-500 italic">Not yet configured</span>
          </li>
        ))}
      </ul>

      <div className="pt-4 border-t border-gray-200">
        <div className="flex justify-between items-center">
          <span className="text-lg font-semibold">Total Price:</span>
          <div className="text-2xl font-bold text-teal-600">
            <PriceDisplay amount={totalPrice} isLarge />
          </div>
        </div>

        <Button
          className="w-full mt-6 bg-teal-600 hover:bg-teal-700 flex items-center justify-center gap-2"
          onClick={onAddToCart}
          disabled={!isConfigurationComplete}
        >
          <ShoppingCart className="h-4 w-4" />
          Add to Cart
        </Button>
      </div>
    </div>
  )
}

// Component to display price with currency conversion
function PriceDisplay({ amount, isLarge = false }: { amount: number; isLarge?: boolean }) {
  const { formattedPrice, isConverting } = useConvertedPrice({ amount })
  
  if (isConverting) {
    return (
      <span className="inline-flex items-center">
        <Loader2 className={`h-4 w-4 mr-1 animate-spin ${isLarge ? 'h-5 w-5' : 'h-4 w-4'}`} />
      </span>
    )
  }
  
  return <span>{formattedPrice}</span>
}
