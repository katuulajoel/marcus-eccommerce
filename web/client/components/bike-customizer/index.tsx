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

interface BikeCustomizerProps {
  productId?: string
  category: string
}

export default function BikeCustomizer({ productId, category }: BikeCustomizerProps) {
  const { toast } = useToast()
  const { addItem } = useCart()
  
  const [categoryId, setCategoryId] = useState<number | null>(null)
  const [parts, setParts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

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

  // Effect to load categories and find the category ID
  useEffect(() => {
    const getCategory = async () => {
      try {
        if (!category) return

        const categories = await fetchCategories()
        const matchedCategory = categories.find(
          (cat) => cat.name.toLowerCase() === category.toLowerCase(),
        )

        if (matchedCategory) {
          setCategoryId(matchedCategory.id)
        } else {
          setError(`Category "${category}" not found.`)
        }
      } catch (err) {
        console.error("Failed to fetch categories:", err)
        setError("Failed to load category information.")
      }
    }

    getCategory()
  }, [category])

  // Effect to load parts and options when categoryId changes
  useEffect(() => {
    const loadPartsAndOptions = async () => {
      if (!categoryId) return

      setLoading(true)
      try {
        const partsData = await fetchPartsWithOptions(categoryId)
        setParts(partsData)
      } catch (err) {
        console.error("Failed to load parts:", err)
        setError("Failed to load product parts. Please try again later.")
      } finally {
        setLoading(false)
      }
    }

    loadPartsAndOptions()
  }, [categoryId])

  // Add the product to cart
  const addToCart = () => {
    const uniqueId = `${productId}-${Date.now()}`
    const configDetails = getConfigDetails()

    addItem({
      id: uniqueId,
      name: preConfiguredProduct?.name || 'Custom Product',
      price: totalPrice,
      image: preConfiguredProduct?.image_url,
      quantity: 1,
      configuration: { ...configuration },
      configDetails,
    })

    toast({
      title: "Added to cart",
      description: `${preConfiguredProduct?.name || 'Custom Product'} has been added to your cart.`,
    })
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <Loader2 className="h-10 w-10 text-teal-600 animate-spin mb-4" />
        <p className="text-lg text-gray-600">Loading product options...</p>
      </div>
    )
  }

  if (error) {
    return (
      <Alert variant="destructive" className="mb-6">
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )
  }

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
