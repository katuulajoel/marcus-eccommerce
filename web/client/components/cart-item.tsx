import { Trash2, Plus, Minus } from "lucide-react"
import { Button } from "@shared/components/ui/button"
import { useConvertedPrice } from "@shared/hooks/use-converted-price"
import type { CartItem as CartItemType } from "@client/context/cart-context"

interface CartItemProps {
  item: CartItemType
  onQuantityChange: (id: string, quantity: number) => void
  onRemove: (id: string) => void
}

export default function CartItem({ item, onQuantityChange, onRemove }: CartItemProps) {
  const { formattedPrice: itemPrice, isConverting: isItemPriceLoading } = useConvertedPrice({ amount: item.price })

  return (
    <div className="p-6 border-b">
      <div className="flex flex-col md:flex-row gap-6">
        <div className="relative h-40 w-full md:w-40 bg-gray-50 rounded-md">
          <img
            src={item.image || "/placeholder.svg"}
            alt={item.name}
            className="object-contain p-2 h-full w-full"
          />
        </div>
        <div className="flex-1">
          <div className="flex justify-between">
            <h3 className="text-lg font-semibold">{item.name}</h3>
            <p className="text-lg font-bold text-teal-600">
              {isItemPriceLoading ? 'Loading...' : itemPrice}
            </p>
          </div>

          {item.configDetails && (
            <div className="mt-2 space-y-1">
              {Object.entries(item.configDetails).map(([category, details]) => (
                <div key={category} className="flex justify-between text-sm">
                  <span className="text-gray-600">
                    {category.replace(/([A-Z])/g, " $1").replace(/^./, (str) => str.toUpperCase())}:
                  </span>
                  <span>{details.name}</span>
                </div>
              ))}
            </div>
          )}

          <div className="mt-4 flex items-center justify-between">
            <div className="flex items-center">
              <Button
                variant="outline"
                size="icon"
                onClick={() => onQuantityChange(item.id, item.quantity - 1)}
                disabled={item.quantity <= 1}
              >
                <Minus className="h-4 w-4" />
              </Button>
              <span className="mx-4 font-semibold">{item.quantity}</span>
              <Button
                variant="outline"
                size="icon"
                onClick={() => onQuantityChange(item.id, item.quantity + 1)}
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onRemove(item.id)}
              className="text-red-500 hover:text-red-700"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Remove
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
