"use client"

import { useState, useEffect } from "react"
import { AlertCircle, ChevronRight, Check, ShoppingCart, Loader2 } from "lucide-react"
import { Button } from "@shared/components/ui/button"
import { RadioGroup, RadioGroupItem } from "@shared/components/ui/radio-group"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@shared/components/ui/tabs"
import { Card, CardContent } from "@shared/components/ui/card"
import { Badge } from "@shared/components/ui/badge"
import { Alert, AlertDescription } from "@shared/components/ui/alert"
import { cn } from "@shared/lib/utils"
import { useToast } from "@shared/components/ui/use-toast"
import { useCart } from "@client/context/cart-context"
import { fetchCategories, fetchPartsWithOptions } from "@client/services/api"

interface BikeCustomizerProps {
  initialConfiguration?: {
    [key: string]: string
  } | null
  productName?: string
  productImage?: string
  productId?: string
  category?: string
}

export default function BikeCustomizer({
  initialConfiguration = null,
  productName = "Custom Product",
  productImage = "/placeholder.svg?height=300&width=400",
  productId = "custom-product",
  category = "bicycles",
}: BikeCustomizerProps) {
  const { toast } = useToast()
  const { addItem } = useCart()

  // State for API data
  const [categoryId, setCategoryId] = useState<number | null>(null)
  const [parts, setParts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // State for customization
  const [activeTab, setActiveTab] = useState<string>("")
  const [configuration, setConfiguration] = useState<{ [key: string]: string }>({})
  const [totalPrice, setTotalPrice] = useState(0)

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

        // Sort parts by step order (already sorted by the API)
        setParts(partsData)

        // Set the first part as active if we have parts
        if (partsData.length > 0) {
          setActiveTab(partsData[0].name)
        }

        // Initialize configuration with first option of each part
        initializeConfiguration(partsData)
      } catch (err) {
        console.error("Failed to load parts:", err)
        setError("Failed to load product parts. Please try again later.")
      } finally {
        setLoading(false)
      }
    }

    loadPartsAndOptions()
  }, [categoryId])

  // Initialize configuration based on whether we have a preconfigured product
  const initializeConfiguration = (parts: any[]) => {
    const initialConfig: { [key: string]: string } = {}

    if (initialConfiguration) {
      // If we have a preconfigured product, use its configuration
      Object.keys(initialConfiguration).forEach((key) => {
        const part = parts.find((p) => p.name === key)
        if (part && part.options.some((opt) => opt.id.toString() === initialConfiguration[key])) {
          initialConfig[key] = initialConfiguration[key]
        }
      })
    } else {
      // If creating from scratch, only initialize the first part (if any)
      // to give the user a starting point
      if (parts.length > 0 && parts[0].options && parts[0].options.length > 0) {
        initialConfig[parts[0].name] = parts[0].options[0].id.toString()
      }
    }

    setConfiguration(initialConfig)
  }

  // Calculate total price whenever configuration changes
  useEffect(() => {
    if (Object.keys(configuration).length === 0) return

    let price = 0

    // Add the price of each selected option
    Object.entries(configuration).forEach(([partName, optionId]) => {
      const part = parts.find((p) => p.name === partName)
      if (!part) return

      const option = part.options.find((opt) => opt.id.toString() === optionId)
      if (option) {
        price += parseFloat(option.default_price)
      }
    })

    setTotalPrice(price)
  }, [configuration, parts])

  // Function to handle configuration changes
  const handleConfigChange = (partName: string, optionId: string) => {
    setConfiguration((prev) => ({
      ...prev,
      [partName]: optionId,
    }))
  }

  // Function to move to the next part
  const goToNextPart = () => {
    const currentIndex = parts.findIndex((part) => part.name === activeTab)
    if (currentIndex < parts.length - 1) {
      const nextPart = parts[currentIndex + 1]
      setActiveTab(nextPart.name)

      // If the next part doesn't have a selection yet and has options,
      // automatically select the first option
      if (!configuration[nextPart.name] && nextPart.options && nextPart.options.length > 0) {
        setConfiguration((prev) => ({
          ...prev,
          [nextPart.name]: nextPart.options[0].id.toString(),
        }))
      }
    }
  }

  // Get the current part description
  const getCurrentPartDescription = () => {
    const part = parts.find((p) => p.name === activeTab)
    const option = part?.options.find((opt) => opt.id.toString() === configuration[part?.name])
    return option?.description || part?.description || ""
  }

  // Get option details
  const getOptionDetails = (partName: string, optionId: string) => {
    const part = parts.find((p) => p.name === partName)
    if (!part) return null

    return part.options.find((opt) => opt.id.toString() === optionId)
  }

  // Get image for the selected option
  const getOptionImage = (partName: string, optionId: string) => {
    const option = getOptionDetails(partName, optionId)
    return option?.image_url || "/placeholder.svg?height=150&width=150"
  }

  // Get the image for the current configuration based on active part - simplified
  const getCurrentImage = () => {
    // Try to use the active part's selected option's image
    const activePart = parts.find(p => p.name === activeTab)
    if (activePart && configuration[activeTab]) {
      const activeOption = activePart.options.find(opt => opt.id.toString() === configuration[activeTab])
      if (activeOption?.image_url) {
        return activeOption.image_url
      }
    }
    
    // Fall back directly to product image or placeholder
    return productImage || "/placeholder.svg?height=300&width=400"
  }

  // Create configuration details object for cart
  const getConfigDetails = () => {
    const details: { [key: string]: { name: string; price: number } } = {}

    Object.entries(configuration).forEach(([partName, optionId]) => {
      const option = getOptionDetails(partName, optionId)
      if (option) {
        details[partName] = {
          name: option.name,
          price: parseFloat(option.default_price),
        }
      }
    })

    return details
  }

  // Add the product to cart
  const addToCart = () => {
    const uniqueId = `${productId}-${Date.now()}`

    addItem({
      id: uniqueId,
      name: productName,
      price: totalPrice,
      image: productImage,
      quantity: 1,
      configuration: { ...configuration },
      configDetails: getConfigDetails(),
    })

    toast({
      title: "Added to cart",
      description: `${productName} has been added to your cart.`,
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
      {/* Header with product info */}
      <div className="bg-white rounded-lg border shadow-sm p-6 flex flex-col md:flex-row gap-6 items-center">
        {productImage && (
          <div className="relative w-full md:w-1/3 h-[200px]">
            <img
              src={productImage || "/placeholder.svg"}
              alt={productName}
              className="object-contain w-full h-full"
            />
          </div>
        )}
        <div className="md:w-2/3">
          <h2 className="text-2xl font-bold mb-2">Build Your Dream Product</h2>
          <p className="text-gray-600 mb-4">
            {productName !== "Custom Product" ? (
              <>
                You're customizing the <span className="font-semibold">{productName}</span>. Feel free to modify any
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

      {/* Main customization area */}
      <div className="grid md:grid-cols-5 gap-8">
        {/* Left side: Product visualization */}
        <div className="md:col-span-2 bg-white rounded-lg border shadow-sm p-6">
          <div className="bg-gray-50 p-4 rounded-lg mb-6">
            <div className="relative w-full h-[300px] mx-auto">
              <img
                src={getCurrentImage()}
                alt={productName}
                className="object-contain w-full h-full"
              />
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-xl font-semibold">Configuration Summary</h3>
            <ul className="space-y-3">
              {Object.entries(configuration).map(([partName, optionId]) => {
                const option = getOptionDetails(partName, optionId)
                if (!option) return null

                return (
                  <li key={partName} className="flex justify-between items-center py-2 border-b">
                    <span className="text-gray-600">{partName}</span>
                    <div className="flex items-center">
                      <span className="font-medium mr-4">{option.name}</span>
                      <span className="text-teal-600 font-semibold">
                        {parseFloat(option.default_price) > 0 ? `$${option.default_price}` : "Included"}
                      </span>
                    </div>
                  </li>
                )
              })}

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
                <span className="text-2xl font-bold text-teal-600">${totalPrice.toLocaleString()}</span>
              </div>

              <Button
                className="w-full mt-6 bg-teal-600 hover:bg-teal-700 flex items-center justify-center gap-2"
                onClick={addToCart}
              >
                <ShoppingCart className="h-4 w-4" />
                Add to Cart
              </Button>
            </div>
          </div>
        </div>

        {/* Right side: Part selection */}
        <div className="md:col-span-3 bg-white rounded-lg border shadow-sm p-6">
          {/* Part description */}
          <div className="mb-6">
            <p className="text-gray-600">{getCurrentPartDescription()}</p>
          </div>

          {/* Tabs for part selection */}
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
                    <p className="text-gray-500">Select your preferred option</p>
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

                <RadioGroup
                  value={configuration[part.name] || ""}
                  onValueChange={(value) => handleConfigChange(part.name, value)}
                  className="grid grid-cols-1 md:grid-cols-3 gap-6"
                >
                  {part.options?.map((option) => {
                    // For now, all options are compatible
                    const compatible = true
                    const optionId = option.id.toString()

                    return (
                      <Card
                        key={optionId}
                        className={cn(
                          "relative overflow-hidden transition-all",
                          configuration[part.name] === optionId ? "ring-2 ring-teal-600" : "border",
                          !compatible ? "opacity-60" : "hover:shadow-md",
                        )}
                      >
                        <div
                          className={cn(
                            "absolute inset-0 z-0",
                            configuration[part.name] === optionId ? "bg-teal-50" : "bg-transparent",
                          )}
                        />

                        <RadioGroupItem
                          value={optionId}
                          id={`${part.name}-${optionId}`}
                          className="sr-only peer"
                          disabled={!compatible}
                        />

                        <label
                          htmlFor={`${part.name}-${optionId}`}
                          className={cn(
                            "flex flex-col h-full cursor-pointer z-10 relative",
                            !compatible && "cursor-not-allowed",
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
                                src={getOptionImage(part.name, optionId)}
                                alt={option.name}
                                className="object-contain p-2 w-full h-full"
                              />
                            )}

                            {configuration[part.name] === optionId && (
                              <div className="absolute top-2 right-2 bg-teal-600 text-white rounded-full p-1">
                                <Check className="h-4 w-4" />
                              </div>
                            )}
                          </div>

                          <CardContent className="p-4 flex-grow flex flex-col">
                            <div className="flex items-start justify-between mb-2">
                              <h4 className="font-medium text-lg">{option.name}</h4>
                              <span className="text-teal-600 font-semibold">
                                {parseFloat(option.default_price) > 0 ? `+$${option.default_price}` : "Included"}
                              </span>
                            </div>

                            <p className="text-sm text-gray-500 mb-3 flex-grow">
                              {option.description || "No description available"}
                            </p>
                          </CardContent>
                        </label>
                      </Card>
                    )
                  })}
                </RadioGroup>
              </TabsContent>
            ))}
          </Tabs>
        </div>
      </div>
    </div>
  )
}

