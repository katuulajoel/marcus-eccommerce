import { Check, AlertCircle } from "lucide-react"
import { Card, CardContent } from "@shared/components/ui/card"
import { RadioGroupItem } from "@shared/components/ui/radio-group"
import { cn } from "@shared/lib/utils"

interface OptionCardProps {
  part: any
  option: any
  isSelected: boolean
  isCompatible: boolean
  isInStock: boolean
  isLowStock: boolean
  incompatibilityMessage?: string
  stockQuantity: number
  formattedPrice: string
  disabled: boolean
}

export function OptionCard({
  part,
  option,
  isSelected,
  isCompatible,
  isInStock,
  isLowStock,
  incompatibilityMessage,
  stockQuantity,
  formattedPrice,
  disabled
}: OptionCardProps) {
  const optionId = option.id.toString()
  const isAvailable = isCompatible && isInStock

  return (
    <Card
      className={cn(
        "relative overflow-hidden transition-all",
        isSelected ? "ring-2 ring-teal-600" : "border",
        !isAvailable ? "opacity-60" : "hover:shadow-md",
      )}
    >
      <div
        className={cn(
          "absolute inset-0 z-0",
          isSelected ? "bg-teal-50" : "bg-transparent",
        )}
      />

      {!isInStock && (
        <div className="absolute top-0 right-0 bg-red-500 text-white font-bold py-1 px-3 transform rotate-45 translate-y-2 translate-x-8 z-20">
          Out of Stock
        </div>
      )}

      <RadioGroupItem
        value={optionId}
        id={`${part.name}-${optionId}`}
        className="sr-only peer"
        disabled={disabled}
      />

      <label
        htmlFor={`${part.name}-${optionId}`}
        className={cn(
          "flex flex-col h-full cursor-pointer z-10 relative",
          disabled && "cursor-not-allowed",
        )}
      >
        <div className="relative h-40 bg-gray-50 border-b">
          {part.name.toLowerCase().includes("color") ? (
            <div className="absolute inset-0 flex items-center justify-center">
              <div
                className="h-20 w-20 rounded-full border-4 border-gray-200"
                style={{ backgroundColor: option.color || "#000000" }}
              />
            </div>
          ) : (
            <img
              src={option.image_url || "/placeholder.svg?height=150&width=150"}
              alt={option.name}
              className="object-contain p-2 w-full h-full"
            />
          )}

          {isSelected && (
            <div className="absolute top-2 right-2 bg-teal-600 text-white rounded-full p-1">
              <Check className="h-4 w-4" />
            </div>
          )}
        </div>

        <CardContent className="p-4 flex-grow flex flex-col">
          <div className="flex items-start justify-between mb-2">
            <h4 className="font-medium text-lg">{option.name}</h4>
            <span className="text-teal-600 font-semibold">
              {formattedPrice}
            </span>
          </div>

          <p className="text-sm text-gray-500 mb-3 flex-grow">
            {option.description || "No description available"}
          </p>

          {/* Stock status indicator */}
          <div className={cn(
            "text-sm font-medium flex items-center",
            !isInStock ? "text-red-600" : isLowStock ? "text-amber-600" : "text-green-600"
          )}>
            <span className={cn(
              "w-2 h-2 rounded-full mr-2",
              !isInStock ? "bg-red-600" : isLowStock ? "bg-amber-600" : "bg-green-600"
            )}></span>
            {isInStock 
              ? isLowStock 
                ? `Low stock (${stockQuantity})`
                : `In stock (${stockQuantity})`
              : "Out of stock"
            }
          </div>

          {!isCompatible && (
            <div className="flex items-center text-amber-600 mt-1 text-sm">
              <AlertCircle className="h-3 w-3 mr-1" />
              {incompatibilityMessage || "Not compatible with current configuration"}
            </div>
          )}
        </CardContent>
      </label>
    </Card>
  )
}
