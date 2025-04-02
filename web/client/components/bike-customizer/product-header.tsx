import { Badge } from "@shared/components/ui/badge"

interface ProductHeaderProps {
  preConfiguredProduct: any
  configuration: { [key: string]: string }
  getOptionDetails: (partName: string, optionId: string) => any
}

export function ProductHeader({
  preConfiguredProduct,
  configuration,
  getOptionDetails
}: ProductHeaderProps) {
  return (
    <div className="bg-white rounded-lg border shadow-sm p-6 flex flex-col md:flex-row gap-6 items-center">
      {preConfiguredProduct && (
        <div className="relative w-full md:w-1/3 h-[200px]">
          <img
            src={preConfiguredProduct.image_url || "/placeholder.svg"}
            alt={preConfiguredProduct.name}
            className="object-contain w-full h-full"
          />
        </div>
      )}
      <div className="md:w-2/3">
        <h2 className="text-2xl font-bold mb-2">Build Your Dream Product</h2>
        <p className="text-gray-600 mb-4">
          {preConfiguredProduct ? (
            <>
              You're customizing the <span className="font-semibold">{preConfiguredProduct.name}</span>. Feel free to modify any
              options to create your perfect product.
            </>
          ) : (
            "Customize every aspect of your product to create the perfect item for your style and needs."
          )}
        </p>
        <div className="flex flex-wrap gap-2">
          {Object.entries(configuration).map(([partName, optionId]) => {
            const option = getOptionDetails(partName, optionId)
            if (!option) return null

            return (
              <Badge key={partName} variant="outline" className="bg-white">
                {option.name}
              </Badge>
            )
          })}
        </div>
      </div>
    </div>
  )
}
