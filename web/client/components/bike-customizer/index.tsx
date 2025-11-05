"use client"

import { useState, useEffect } from "react"
import { Loader2 } from "lucide-react"
import { Alert, AlertDescription } from "@shared/components/ui/alert"
import { useToast } from "@shared/components/ui/use-toast"
import { useCart } from "@client/context/cart-context"
import { fetchCategories, fetchPartsWithOptions } from "@client/services/api"
import { ConfigSummary } from "./config-summary"
import { PartSelector } from "./part-selector"
import { ProductHeader } from "./product-header"
import { useProductConfiguration } from "@client/hooks/use-product-configuration"
import { useProductRules } from "@client/hooks/use-product-rules"
import { useProductStock } from "@client/hooks/use-product-stock"
import { useQuery } from "@tanstack/react-query"

interface BikeCustomizerProps {
  productId?: string
  category: string
}

export default function BikeCustomizer({ productId, category }: BikeCustomizerProps) {
  const { toast } = useToast()
  const { addItem } = useCart()
  
  const [categoryId, setCategoryId] = useState<number | null>(null)

  // Use React Query to fetch categories
  const { 
    data: categories, 
    isLoading: isLoadingCategories, 
    error: categoriesError 
  } = useQuery({
    queryKey: ["categories"],
    queryFn: fetchCategories,
  })

  // Find category ID when categories are loaded
  useEffect(() => {
    if (!categories || !category) return

    const matchedCategory = categories.find(
      (cat) => cat.name.toLowerCase() === category.toLowerCase()
    )

    if (matchedCategory) {
      setCategoryId(matchedCategory.id)
    }
  }, [categories, category])

  // Use React Query to fetch parts based on categoryId
  const {
    data: parts = [],
    isLoading: isLoadingParts,
    error: partsError
  } = useQuery({
    queryKey: ["parts", categoryId],
    queryFn: () => categoryId ? fetchPartsWithOptions(categoryId) : Promise.resolve([]),
    enabled: !!categoryId,
  })

  const { 
    configuration, 
    activeTab, 
    preConfiguredProduct,
    setActiveTab, 
    handleConfigChange, 
    goToNextPart,
    getOptionDetails,
    getCurrentPartDescription, 
    getCurrentImage,
    isConfigurationComplete
  } = useProductConfiguration(productId, categoryId, parts)
  
  const {
    incompatibilityMessages,
    totalPrice,
    isCompatible,
    getFormattedPriceDisplay,
    getConfigDetails
  } = useProductRules(configuration, parts)
  
  const {
    isInStock,
    isLowStock,
    getStockQuantity
  } = useProductStock(categoryId)

  // Add the product to cart
  const addToCart = () => {
    // Use productId if available, otherwise use categoryId as fallback
    const itemId = productId || `custom-${categoryId}-${Date.now()}`
    const configDetails = getConfigDetails()

    addItem({
      id: itemId,
      name: preConfiguredProduct?.name || 'Custom Product',
      price: totalPrice,
      image: preConfiguredProduct?.image_url || '/placeholder.png',
      quantity: 1,
      categoryId: categoryId || undefined,
      configuration: { ...configuration },
      configDetails,
    })

    toast({
      title: "Added to cart",
      description: `${preConfiguredProduct?.name || 'Custom Product'} has been added to your cart.`,
    })
  }

  // Handle loading states
  const isLoading = isLoadingCategories || isLoadingParts
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <Loader2 className="h-10 w-10 text-teal-600 animate-spin mb-4" />
        <p className="text-lg text-gray-600">Loading product options...</p>
      </div>
    )
  }

  // Handle errors
  const error = categoriesError || partsError
  if (error) {
    return (
      <Alert variant="destructive" className="mb-6">
        <AlertDescription>
          {error instanceof Error ? error.message : "Failed to load product data"}
        </AlertDescription>
      </Alert>
    )
  }

  // Handle category not found
  if (categories && !categoryId) {
    return (
      <Alert variant="destructive" className="mb-6">
        <AlertDescription>
          {`Category "${category}" not found.`}
        </AlertDescription>
      </Alert>
    )
  }

  // Handle no parts available
  if (parts.length === 0) {
    return (
      <div className="text-center py-10">
        <p className="text-gray-500">No customization options found for this product category.</p>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Product header */}
      <ProductHeader 
        preConfiguredProduct={preConfiguredProduct}
        configuration={configuration}
        getOptionDetails={getOptionDetails}
      />

      {/* Main customization area */}
      <div className="grid md:grid-cols-5 gap-8">
        {/* Left side: Product visualization */}
        <div className="md:col-span-2 bg-white rounded-lg border shadow-sm p-6">
          <ConfigSummary
            configuration={configuration}
            parts={parts}
            configDetails={getConfigDetails()}
            totalPrice={totalPrice}
            isConfigurationComplete={isConfigurationComplete()}
            productName={preConfiguredProduct?.name}
            onAddToCart={addToCart}
            currentImage={getCurrentImage()}
          />
        </div>

        {/* Right side: Part selection */}
        <div className="md:col-span-3 bg-white rounded-lg border shadow-sm p-6">
          <PartSelector
            parts={parts}
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            configuration={configuration}
            handleConfigChange={handleConfigChange}
            goToNextPart={goToNextPart}
            getCurrentPartDescription={getCurrentPartDescription}
            isCompatible={isCompatible}
            incompatibilityMessages={incompatibilityMessages}
            getFormattedPriceDisplay={getFormattedPriceDisplay}
            isInStock={isInStock}
            isLowStock={isLowStock}
            getStockQuantity={getStockQuantity}
          />
        </div>
      </div>
    </div>
  )
}
