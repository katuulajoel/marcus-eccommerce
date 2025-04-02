import { ChevronRight } from "lucide-react"
import { Button } from "@shared/components/ui/button"
import { RadioGroup } from "@shared/components/ui/radio-group"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@shared/components/ui/tabs"
import { cn } from "@shared/lib/utils"
import { OptionCard } from "./option-card"

interface PartSelectorProps {
  parts: any[]
  activeTab: string
  setActiveTab: (tab: string) => void
  configuration: { [key: string]: string }
  handleConfigChange: (partName: string, optionId: string) => void
  goToNextPart: () => void
  getCurrentPartDescription: () => string
  isCompatible: (partName: string, optionId: string) => boolean
  incompatibilityMessages: { [key: string]: string }
  getFormattedPriceDisplay: (option: any) => string
  isInStock: (optionId: number) => boolean
  isLowStock: (optionId: number) => boolean
  getStockQuantity: (optionId: number) => number
}

export function PartSelector({
  parts,
  activeTab,
  setActiveTab,
  configuration,
  handleConfigChange,
  goToNextPart,
  getCurrentPartDescription,
  isCompatible,
  incompatibilityMessages,
  getFormattedPriceDisplay,
  isInStock,
  isLowStock,
  getStockQuantity
}: PartSelectorProps) {
  return (
    <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
      {/* Tab navigation */}
      <TabsList className="w-full grid grid-cols-5 mb-6">
        {parts.map((part) => (
          <TabsTrigger
            key={part.id}
            value={part.name}
            className={cn(activeTab === part.name ? "border-b-2 border-teal-600" : "")}
          >
            {part.name}
          </TabsTrigger>
        ))}
      </TabsList>

      {/* Part options */}
      {parts.map((part) => (
        <TabsContent key={part.id} value={part.name} className="pt-4">
          <div className="mb-4 flex justify-between items-center">
            <div>
              <h3 className="text-xl font-semibold mb-1">{part.name}</h3>
              <p className="text-gray-500">
                {configuration[part.name] 
                  ? "Select your preferred option" 
                  : "Please select an option to continue"}
              </p>
            </div>
            {part.step !== parts[parts.length - 1].step && (
              <Button
                onClick={goToNextPart}
                className="bg-teal-600 hover:bg-teal-700"
                disabled={!configuration[part.name]} // Disable if no selection made
              >
                Next <ChevronRight className="ml-1 h-4 w-4" />
              </Button>
            )}
          </div>

          <p className="text-gray-600 mb-6">{getCurrentPartDescription()}</p>

          <RadioGroup
            value={configuration[part.name] || ""}
            onValueChange={(value) => handleConfigChange(part.name, value)}
            className="grid grid-cols-1 md:grid-cols-3 gap-6"
          >
            {part.options?.map((option) => {
              const optionId = option.id.toString()
              const optionIdNum = parseInt(optionId, 10)
              const compatible = isCompatible(part.name, optionId)
              const inStock = isInStock(optionIdNum)
              const lowStock = isLowStock(optionIdNum)
              const stockQuantity = getStockQuantity(optionIdNum)
              const isSelected = configuration[part.name] === optionId
              const isAvailable = compatible && inStock
              
              return (
                <OptionCard
                  key={optionId}
                  part={part}
                  option={option}
                  isSelected={isSelected}
                  isCompatible={compatible}
                  isInStock={inStock}
                  isLowStock={lowStock}
                  incompatibilityMessage={incompatibilityMessages[`${part.name}-${optionId}`]}
                  stockQuantity={stockQuantity}
                  formattedPrice={getFormattedPriceDisplay(option)}
                  disabled={!isAvailable}
                />
              )
            })}
          </RadioGroup>
        </TabsContent>
      ))}
    </Tabs>
  )
}
