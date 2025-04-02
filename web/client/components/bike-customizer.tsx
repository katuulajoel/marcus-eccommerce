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
import { 
  fetchCategories, 
  fetchPartsWithOptions, 
  fetchIncompatibilityRules,
  fetchPriceAdjustmentRules,
  fetchCategoryStock
} from "@client/services/api"

interface BikeCustomizerProps {
  initialConfiguration?: {
    [key: string]: string
  } | null
  productName?: string
  productImage?: string
  productId?: string
  category?: string
}

interface StockInfo {
  id: number
  quantity: number
  part_option: number
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
  const [stockInfo, setStockInfo] = useState<StockInfo[]>([])

  // State for customization
  const [activeTab, setActiveTab] = useState<string>("")
  const [configuration, setConfiguration] = useState<{ [key: string]: string }>({})
  const [totalPrice, setTotalPrice] = useState(0)

  // State for incompatibility rules
  const [incompatibilityRules, setIncompatibilityRules] = useState<any[]>([])
  const [incompatibilityMessages, setIncompatibilityMessages] = useState<{ [key: string]: string }>({})

  // Add state for price adjustment rules and adjusted prices
  const [priceAdjustmentRules, setPriceAdjustmentRules] = useState<any[]>([])
  const [adjustedPrices, setAdjustedPrices] = useState<{ [key: number]: number }>({})

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

  // Fetch stock information when component mounts AND when categoryId changes
  useEffect(() => {
    if (!categoryId) return;

    const getStockInfo = async () => {
      try {
        const stockData = await fetchCategoryStock(categoryId)
        setStockInfo(stockData)
      } catch (err) {
        console.error("Failed to fetch stock information:", err)
        // No need to set error state - we can still function without stock info
      }
    }

    getStockInfo()
  }, [categoryId])

  // Fetch incompatibility rules when component mounts
  useEffect(() => {
    const getIncompatibilityRules = async () => {
      try {
        const rulesData = await fetchIncompatibilityRules()
        setIncompatibilityRules(rulesData)
      } catch (err) {
        console.error("Failed to fetch incompatibility rules:", err)
      }
    }

    getIncompatibilityRules()
  }, [])

  // Fetch price adjustment rules when component mounts
  useEffect(() => {
    const getPriceAdjustmentRules = async () => {
      try {
        const rulesData = await fetchPriceAdjustmentRules()
        setPriceAdjustmentRules(rulesData)
      } catch (err) {
        console.error("Failed to fetch price adjustment rules:", err)
      }
    }

    getPriceAdjustmentRules()
  }, [])

  // Add a new useEffect to calculate incompatibility messages whenever configuration or rules change
  useEffect(() => {
    if (incompatibilityRules.length === 0 || parts.length === 0) return;

    const newIncompatibilityMessages: { [key: string]: string } = {};

    // For each part and its options
    parts.forEach((part) => {
      if (!part.options) return;

      // Check each option against the current configuration
      part.options.forEach((option) => {
        const optionId = option.id.toString();

        // Check this option against all selected options in the configuration
        Object.entries(configuration).forEach(([configPartName, selectedOptionId]) => {
          if (!selectedOptionId) return;
          if (part.name === configPartName && optionId === selectedOptionId) return; // Skip checking against self

          // Find the part for this configuration item
          const configPart = parts.find((p) => p.name === configPartName);
          if (!configPart) return;

          // Find the selected option
          const selectedOption = configPart.options.find(
            (opt) => opt.id.toString() === selectedOptionId,
          );
          if (!selectedOption) return;

          // Check for incompatibilities between these two options
          for (const rule of incompatibilityRules) {
            const isThisOptionInRule =
              rule.part_option === option.id || rule.incompatible_with_option === option.id;
            const isSelectedOptionInRule =
              rule.part_option === selectedOption.id ||
              rule.incompatible_with_option === selectedOption.id;

            if (isThisOptionInRule && isSelectedOptionInRule) {
              newIncompatibilityMessages[`${part.name}-${optionId}`] = rule.message;
            }
          }
        });
      });
    });

    setIncompatibilityMessages(newIncompatibilityMessages);
  }, [configuration, incompatibilityRules, parts]);

  // Calculate adjusted prices whenever configuration or rules change
  useEffect(() => {
    // Skip if we don't have rules or parts data yet
    if (priceAdjustmentRules.length === 0 || parts.length === 0) return
    
    const newAdjustedPrices: { [key: number]: number } = {}
    
    // Convert configuration values to numbers for comparison
    const selectedOptionIds = Object.values(configuration).map(id => parseInt(id, 10))
    
    // Check each rule
    priceAdjustmentRules.forEach(rule => {
      // Ensure we're using the correct field names from the API
      const conditionOptionId = rule.condition_option
      const affectedOptionId = rule.affected_option
      
      // If the condition option is selected
      if (selectedOptionIds.includes(conditionOptionId)) {
        // Find the affected option to get its base price
        let affectedOption = null;
        parts.forEach(part => {
          const foundOption = part.options?.find(opt => opt.id === affectedOptionId);
          if (foundOption) {
            affectedOption = foundOption;
          }
        });
        
        if (affectedOption) {
          // Store the adjusted price value from the rule - not the final price
          // This is the amount to be added to the base price
          newAdjustedPrices[affectedOptionId] = parseFloat(rule.adjusted_price);
        }
      }
    })
    
    setAdjustedPrices(newAdjustedPrices)
  }, [configuration, priceAdjustmentRules, parts])

  // Updated price calculation to consider price adjustments as additions to base price
  useEffect(() => {
    if (Object.keys(configuration).length === 0) return

    let price = 0

    // Add the price of each selected option, considering adjustments
    Object.entries(configuration).forEach(([partName, optionId]) => {
      const part = parts.find((p) => p.name === partName)
      if (!part) return

      const option = part.options.find((opt) => opt.id.toString() === optionId)
      if (option) {
        const optionIdNum = option.id
        const basePrice = parseFloat(option.default_price)
        const adjustment = adjustedPrices[optionIdNum]
        
        // If there's an adjustment, add it to the base price
        if (adjustment !== undefined) {
          price += basePrice + adjustment
        } else {
          price += basePrice
        }
      }
    })

    setTotalPrice(price)
  }, [configuration, parts, adjustedPrices])

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

  // Check stock quantity for a specific option
  const getStockQuantity = (optionId: number): number => {
    const stock = stockInfo.find(item => item.part_option === optionId)
    return stock ? stock.quantity : 0
  }

  // Check if an option is in stock
  const isInStock = (optionId: number): boolean => {
    return getStockQuantity(optionId) > 0
  }

  // Get stock status text - updated thresholds
  const getStockStatusText = (optionId: number): string => {
    const quantity = getStockQuantity(optionId)
    
    if (quantity === 0) {
      return "Out of stock"
    } else if (quantity <= 5) {
      return `Low stock (${quantity})`
    } else {
      return `In stock (${quantity})`
    }
  }

  // Refactor isCompatible to be a pure function with no state updates and consider stock
  const isCompatible = (partName: string, optionId: string): boolean => {
    // If we don't have incompatibility rules yet, consider everything compatible
    if (incompatibilityRules.length === 0) return true;

    // If this option is already in the current configuration, it's compatible
    if (configuration[partName] === optionId) return true;

    // Check if there's an incompatibility message for this option
    return !incompatibilityMessages[`${partName}-${optionId}`];
  };

  // Check if an option is available (both compatible and in stock)
  const isOptionAvailable = (partName: string, optionId: string): boolean => {
    const isCompatibleOption = isCompatible(partName, optionId)
    const isOptionInStock = isInStock(parseInt(optionId, 10))
    
    return isCompatibleOption && isOptionInStock
  }

  // Update handleConfigChange to only update configuration, not incompatibility messages
  const handleConfigChange = (partName: string, optionId: string) => {
    // Only update the configuration - the useEffect will handle incompatibility messages
    setConfiguration((prev) => ({
      ...prev,
      [partName]: optionId,
    }));
  };

  // Updated function to move to the next part without auto-selection
  const goToNextPart = () => {
    const currentIndex = parts.findIndex((part) => part.name === activeTab)
    if (currentIndex < parts.length - 1) {
      const nextPart = parts[currentIndex + 1]
      setActiveTab(nextPart.name)
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
    const activePart = parts.find((p) => p.name === activeTab)
    if (activePart && configuration[activeTab]) {
      const activeOption = activePart.options.find(
        (opt) => opt.id.toString() === configuration[activeTab],
      )
      if (activeOption?.image_url) {
        return activeOption.image_url
      }
    }

    // Fall back directly to product image or placeholder
    return productImage || "/placeholder.svg?height=300&width=400"
  }

  // Get price for an option with adjustments considered
  const getOptionPrice = (option: any) => {
    const optionIdNum = option.id
    const basePrice = parseFloat(option.default_price)
    const adjustment = adjustedPrices[optionIdNum]
    
    if (adjustment !== undefined) {
      return basePrice + adjustment
    }
    return basePrice
  }

  // Simplified price display for an option - just show final price
  const getFormattedPriceDisplay = (option: any) => {
    const optionIdNum = option.id
    const basePrice = parseFloat(option.default_price)
    const adjustment = adjustedPrices[optionIdNum]
    const finalPrice = adjustment !== undefined ? basePrice + adjustment : basePrice
    
    // Simply return the final price with no visual indicators of adjustments
    return finalPrice > 0 ? `+$${finalPrice}` : "Included"
  }
  
  // Update the Configuration Summary display with the same simplified logic
  const getPriceDisplay = (option: any) => {
    const optionIdNum = parseInt(option.id, 10)
    const basePrice = parseFloat(option.default_price)
    const adjustment = adjustedPrices[optionIdNum]
    const finalPrice = adjustment !== undefined ? basePrice + adjustment : basePrice

    // Simply return the final price with no visual indicators of adjustments
    return (
      <span className="text-teal-600 font-semibold">
        {finalPrice > 0 ? `$${finalPrice}` : "Included"}
      </span>
    )
  }

  // Update getConfigDetails to add adjustment to base price
  const getConfigDetails = () => {
    const details: { [key: string]: { name: string; price: number } } = {}

    Object.entries(configuration).forEach(([partName, optionId]) => {
      const option = getOptionDetails(partName, optionId)
      if (option) {
        const optionIdNum = parseInt(option.id, 10)
        const basePrice = parseFloat(option.default_price)
        const adjustment = adjustedPrices[optionIdNum]
        const finalPrice = adjustment !== undefined ? basePrice + adjustment : basePrice
        
        details[partName] = {
          name: option.name,
          price: finalPrice,
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

  // Check if all parts have been configured
  const isConfigurationComplete = () => {
    // If there are no parts, configuration can't be complete
    if (parts.length === 0) return false;
    
    // Check if each part has a corresponding selection in configuration
    return parts.every(part => configuration[part.name] !== undefined);
  };

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
                      {getPriceDisplay(option)}
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
                disabled={!isConfigurationComplete()}
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

                <RadioGroup
                  value={configuration[part.name] || ""}
                  onValueChange={(value) => handleConfigChange(part.name, value)}
                  className="grid grid-cols-1 md:grid-cols-3 gap-6"
                >
                  {part.options?.map((option) => {
                    const optionId = option.id.toString()
                    const optionIdNum = parseInt(optionId, 10)
                    const compatible = isCompatible(part.name, optionId)
                    const incompatibilityMessage = incompatibilityMessages[`${part.name}-${optionId}`]
                    
                    // Check if this option exists in our stock data
                    const stockItem = stockInfo.find(item => item.part_option === optionIdNum)
                    // Get stock quantity (0 if no stock info found)
                    const stockQuantity = stockItem ? stockItem.quantity : 0
                    const inStock = stockQuantity > 0
                    // Update low stock threshold to 5 items
                    const isLowStock = inStock && stockQuantity <= 5
                    const isAvailable = compatible && inStock
                    
                    return (
                      <Card
                        key={optionId}
                        className={cn(
                          "relative overflow-hidden transition-all",
                          configuration[part.name] === optionId ? "ring-2 ring-teal-600" : "border",
                          !isAvailable ? "opacity-60" : "hover:shadow-md",
                        )}
                      >
                        <div
                          className={cn(
                            "absolute inset-0 z-0",
                            configuration[part.name] === optionId ? "bg-teal-50" : "bg-transparent",
                          )}
                        />

                        {!inStock && (
                          <div className="absolute top-0 right-0 bg-red-500 text-white font-bold py-1 px-3 transform rotate-45 translate-y-2 translate-x-8 z-20">
                            Out of Stock
                          </div>
                        )}

                        <RadioGroupItem
                          value={optionId}
                          id={`${part.name}-${optionId}`}
                          className="sr-only peer"
                          disabled={!isAvailable}
                        />

                        <label
                          htmlFor={`${part.name}-${optionId}`}
                          className={cn(
                            "flex flex-col h-full cursor-pointer z-10 relative",
                            !isAvailable && "cursor-not-allowed",
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
                                {getFormattedPriceDisplay(option)}
                              </span>
                            </div>

                            <p className="text-sm text-gray-500 mb-3 flex-grow">
                              {option.description || "No description available"}
                            </p>

                            {/* Stock status indicator */}
                            <div className={cn(
                              "text-sm font-medium flex items-center",
                              !inStock ? "text-red-600" : isLowStock ? "text-amber-600" : "text-green-600"
                            )}>
                              <span className={cn(
                                "w-2 h-2 rounded-full mr-2",
                                !inStock ? "bg-red-600" : isLowStock ? "bg-amber-600" : "bg-green-600"
                              )}></span>
                              {inStock 
                                ? isLowStock 
                                  ? `Low stock (${stockQuantity})`
                                  : `In stock (${stockQuantity})`
                                : "Out of stock"
                              }
                            </div>

                            {!compatible && (
                              <div className="flex items-center text-amber-600 mt-1 text-sm">
                                <AlertCircle className="h-3 w-3 mr-1" />
                                {incompatibilityMessage || "Not compatible with current configuration"}
                              </div>
                            )}
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

