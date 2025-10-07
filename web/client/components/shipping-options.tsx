import { RadioGroup, RadioGroupItem } from "@shared/components/ui/radio-group"
import { Label } from "@shared/components/ui/label"
import { Loader2, Truck, Bike, AlertCircle } from "lucide-react"
import { ShippingOption } from "@client/services/shipping-api"

interface ShippingOptionsProps {
  options: ShippingOption[]
  selectedOption: ShippingOption | null
  onSelectOption: (option: ShippingOption) => void
  loading?: boolean
  error?: string | null
}

export default function ShippingOptions({
  options,
  selectedOption,
  onSelectOption,
  loading = false,
  error = null,
}: ShippingOptionsProps) {
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-gray-500">
        <Loader2 className="h-8 w-8 animate-spin mb-2" />
        <p>Calculating shipping options...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-md text-red-700 flex items-start gap-2">
        <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
        <div>
          <p className="font-medium">Shipping Calculation Error</p>
          <p className="text-sm">{error}</p>
        </div>
      </div>
    )
  }

  if (options.length === 0) {
    return (
      <div className="p-4 bg-gray-50 border border-gray-200 rounded-md text-gray-600 text-center">
        <p>No shipping options available. Please select a delivery zone.</p>
      </div>
    )
  }

  const getDeliveryMethodIcon = (method: string) => {
    switch (method) {
      case "boda":
        return <Bike className="h-5 w-5" />
      case "van":
      case "truck":
        return <Truck className="h-5 w-5" />
      default:
        return <Truck className="h-5 w-5" />
    }
  }

  const formatCurrency = (amount: number) => {
    return `UGX ${amount.toLocaleString()}`
  }

  return (
    <div className="space-y-3">
      <h3 className="font-semibold text-lg">Select Shipping Method</h3>

      <RadioGroup
        value={selectedOption?.rate_id.toString() || ""}
        onValueChange={(value) => {
          const option = options.find((opt) => opt.rate_id.toString() === value)
          if (option) {
            onSelectOption(option)
          }
        }}
      >
        {options.map((option) => {
          const isSelected = selectedOption?.rate_id === option.rate_id
          const isExpress = option.service_level === "express"

          return (
            <div
              key={option.rate_id}
              className={`border rounded-lg p-4 cursor-pointer transition-all ${
                isSelected ? "border-teal-600 bg-teal-50" : "border-gray-200 hover:border-teal-300"
              }`}
            >
              <div className="flex items-start gap-3">
                <RadioGroupItem value={option.rate_id.toString()} id={`shipping-${option.rate_id}`} className="mt-1" />

                <Label
                  htmlFor={`shipping-${option.rate_id}`}
                  className="flex-1 cursor-pointer"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      {getDeliveryMethodIcon(option.delivery_method)}
                      <div>
                        <p className="font-semibold">
                          {option.delivery_method_display}
                          {isExpress && (
                            <span className="ml-2 text-xs bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full">
                              EXPRESS
                            </span>
                          )}
                        </p>
                        <p className="text-sm text-gray-600">{option.delivery_time}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-teal-600">{formatCurrency(option.total_cost_ugx)}</p>
                    </div>
                  </div>

                  {/* Cost Breakdown */}
                  <div className="text-xs text-gray-500 space-y-1 ml-7">
                    <div className="flex justify-between">
                      <span>Base shipping:</span>
                      <span>{formatCurrency(option.base_cost_ugx)}</span>
                    </div>
                    {option.helper_fee_ugx > 0 && (
                      <div className="flex justify-between text-amber-700">
                        <span>👷 Helper fee:</span>
                        <span>{formatCurrency(option.helper_fee_ugx)}</span>
                      </div>
                    )}
                    {option.extra_care_fee_ugx > 0 && (
                      <div className="flex justify-between text-amber-700">
                        <span>⚠️ Extra care fee:</span>
                        <span>{formatCurrency(option.extra_care_fee_ugx)}</span>
                      </div>
                    )}
                  </div>

                  {/* Shipment Details */}
                  <div className="mt-3 pt-3 border-t border-gray-200 text-xs space-y-1 ml-7">
                    <div className="flex items-start gap-1">
                      <span className="text-gray-500">📦 Shipment:</span>
                      <span className="text-gray-700">
                        {option.total_weight_kg.toFixed(1)}kg • {option.total_volume_m3.toFixed(3)}m³
                      </span>
                    </div>
                    <div className="flex items-start gap-1">
                      <span className="text-gray-500">📅 Delivery:</span>
                      <span className="text-gray-700">
                        Est. {new Date(option.estimated_delivery_date).toLocaleDateString()}
                      </span>
                    </div>
                  </div>

                  {/* Reasons */}
                  {option.reasons && option.reasons.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <p className="text-xs font-medium text-gray-700 mb-1 ml-7">Delivery method reason:</p>
                      <ul className="text-xs text-gray-600 space-y-1 ml-7">
                        {option.reasons.map((reason, index) => (
                          <li key={index} className="flex items-start gap-1">
                            <span className="text-gray-400">•</span>
                            <span>{reason}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </Label>
              </div>
            </div>
          )
        })}
      </RadioGroup>
    </div>
  )
}
