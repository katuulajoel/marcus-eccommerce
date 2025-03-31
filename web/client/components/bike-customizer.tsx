"use client"

import { useState, useEffect } from "react"
import { AlertCircle, ChevronRight, Check, ShoppingCart } from "lucide-react"
import { Button } from "@shared/components/ui/button"
import { RadioGroup, RadioGroupItem } from "@shared/components/ui/radio-group"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@shared/components/ui/tabs"
import { Card, CardContent } from "@shared/components/ui/card"
import { Badge } from "@shared/components/ui/badge"
import { cn } from "@shared/lib/utils"
import { useToast } from "@shared/components/ui/use-toast"
import { useCart } from "@client/context/cart-context"

// Define the bike configuration options and prices with added images
const bikeOptions = {
  frameType: [
    {
      id: "full-suspension",
      name: "Full-suspension",
      price: 1200,
      image: "/placeholder.svg?height=300&width=400",
      partImage: "/placeholder.svg?height=150&width=150",
      description:
        "Full-suspension frames offer maximum comfort and control on rough terrain with front and rear shock absorption.",
    },
    {
      id: "diamond",
      name: "Diamond",
      price: 900,
      image: "/placeholder.svg?height=300&width=400",
      partImage: "/placeholder.svg?height=150&width=150",
      description:
        "Diamond frames provide a classic design with excellent stiffness and power transfer, ideal for efficiency.",
    },
    {
      id: "step-through",
      name: "Step-through",
      price: 850,
      image: "/placeholder.svg?height=300&width=400",
      partImage: "/placeholder.svg?height=150&width=150",
      description:
        "Step-through frames allow easy mounting and dismounting, perfect for urban riding and casual cyclists.",
    },
  ],
  frameFinish: [
    {
      id: "matte",
      name: "Matte",
      price: 100,
      partImage: "/placeholder.svg?height=150&width=150",
      description: "Matte finish provides a sophisticated, non-reflective look that hides minor scratches.",
    },
    {
      id: "shiny",
      name: "Shiny",
      price: 150,
      partImage: "/placeholder.svg?height=150&width=150",
      description: "Shiny finish gives a glossy, eye-catching appearance that makes your bike stand out.",
    },
  ],
  wheels: [
    {
      id: "road",
      name: "Road wheels",
      price: 300,
      partImage: "/placeholder.svg?height=150&width=150",
      description: "Road wheels are lightweight and aerodynamic, designed for speed and efficiency on paved surfaces.",
    },
    {
      id: "mountain",
      name: "Mountain wheels",
      price: 350,
      partImage: "/placeholder.svg?height=150&width=150",
      description: "Mountain wheels are durable and wide, providing excellent traction and stability on rough terrain.",
    },
    {
      id: "fat",
      name: "Fat bike wheels",
      price: 450,
      partImage: "/placeholder.svg?height=150&width=150",
      description:
        "Fat bike wheels offer maximum surface area for superior traction in snow, sand, and extremely loose terrain.",
    },
  ],
  rimColor: [
    {
      id: "red",
      name: "Red",
      price: 50,
      color: "#ef4444",
      partImage: "/placeholder.svg?height=150&width=150",
      description: "Vibrant red rims add a bold, energetic accent to your bike.",
    },
    {
      id: "black",
      name: "Black",
      price: 0,
      color: "#000000",
      partImage: "/placeholder.svg?height=150&width=150",
      description: "Classic black rims provide a timeless, versatile look that matches any frame.",
    },
    {
      id: "blue",
      name: "Blue",
      price: 50,
      color: "#3b82f6",
      partImage: "/placeholder.svg?height=150&width=150",
      description: "Cool blue rims create a distinctive appearance that stands out from the crowd.",
    },
  ],
  chain: [
    {
      id: "single-speed",
      name: "Single-speed chain",
      price: 80,
      partImage: "/placeholder.svg?height=150&width=150",
      description: "Single-speed chains offer simplicity, low maintenance, and a clean look for urban riding.",
    },
    {
      id: "8-speed",
      name: "8-speed chain",
      price: 120,
      partImage: "/placeholder.svg?height=150&width=150",
      description: "8-speed chains provide versatility with multiple gears to handle various terrains and gradients.",
    },
  ],
}

// Define compatibility rules
const compatibilityRules = {
  frameType: {
    "full-suspension": {
      wheels: ["mountain", "fat"],
      chain: ["8-speed"],
    },
    diamond: {
      wheels: ["road", "mountain"],
      chain: ["single-speed", "8-speed"],
    },
    "step-through": {
      wheels: ["road"],
      chain: ["single-speed"],
    },
  },
  wheels: {
    fat: {
      frameType: ["full-suspension"],
    },
  },
}

// Part order and display names for the bike visualization
const partOrder = [
  {
    key: "frameType",
    name: "Frame Type",
    description: "The main structure of your bike that determines its overall shape and riding style.",
  },
  {
    key: "frameFinish",
    name: "Frame Finish",
    description: "The surface treatment that affects both appearance and durability of your frame.",
  },
  {
    key: "wheels",
    name: "Wheels",
    description: "The type of wheels affects how your bike handles different terrains and conditions.",
  },
  { key: "rimColor", name: "Rim Color", description: "Customize the look of your wheels with different rim colors." },
  {
    key: "chain",
    name: "Chain",
    description: "The drivetrain component that transfers power from the pedals to the wheels.",
  },
]

interface BikeCustomizerProps {
  initialConfiguration?: {
    frameType: string
    frameFinish: string
    wheels: string
    rimColor: string
    chain: string
  } | null
  productName?: string
  productImage?: string
  productId?: string
}

export default function BikeCustomizer({
  initialConfiguration = null,
  productName = "Custom Bike",
  productImage = "/placeholder.svg?height=300&width=400",
  productId = "custom-bike",
}: BikeCustomizerProps) {
  const [configuration, setConfiguration] = useState(
    initialConfiguration || {
      frameType: "diamond",
      frameFinish: "matte",
      wheels: "road",
      rimColor: "black",
      chain: "single-speed",
    },
  )

  const [totalPrice, setTotalPrice] = useState(0)
  const [focusedPart, setFocusedPart] = useState<string | null>("frameType")
  const [activeTab, setActiveTab] = useState("frameType")
  const { toast } = useToast()
  const { addItem } = useCart()

  // Check if an option is compatible with the current configuration
  const isCompatible = (category, optionId) => {
    // If there are no specific rules for this category, it's compatible
    if (!compatibilityRules[category]) {
      return true
    }

    // For categories like "wheels" that have rules for specific options
    if (compatibilityRules[category][optionId]) {
      // Check if the current frameType is compatible with this option
      const allowedFrameTypes = compatibilityRules[category][optionId].frameType
      if (allowedFrameTypes && !allowedFrameTypes.includes(configuration.frameType)) {
        return false
      }
    }

    // For frameType compatibility rules
    if (category === "wheels" || category === "chain") {
      // Check if the current frameType has restrictions for this category
      const frameTypeRules = compatibilityRules.frameType[configuration.frameType]
      if (frameTypeRules && frameTypeRules[category]) {
        return frameTypeRules[category].includes(optionId)
      }
    }

    // If no specific rules apply, it's compatible
    return true
  }

  // Handle configuration changes
  const handleConfigChange = (category, value) => {
    // Create a new configuration object
    const newConfig = { ...configuration, [category]: value }

    // Check if we need to update other options for compatibility
    Object.keys(compatibilityRules).forEach((ruleCategory) => {
      if (ruleCategory === category && compatibilityRules[ruleCategory][value]) {
        // This category has rules that might affect other categories
        Object.entries(compatibilityRules[ruleCategory][value]).forEach(([affectedCategory, allowedValues]) => {
          // If the current value for the affected category is not allowed, change it to the first allowed value
          if (!allowedValues.includes(newConfig[affectedCategory])) {
            newConfig[affectedCategory] = allowedValues[0]
          }
        })
      }
    })

    setConfiguration(newConfig)
  }

  // Calculate total price whenever configuration changes
  useEffect(() => {
    let price = 0

    // Add the price of each selected option
    Object.entries(configuration).forEach(([category, selectedId]) => {
      const option = bikeOptions[category]?.find((opt) => opt.id === selectedId)
      if (option) {
        price += option.price
      }
    })

    setTotalPrice(price)
  }, [configuration])

  // Get the current frame image based on the selected frame type
  const getCurrentFrameImage = () => {
    const frameOption = bikeOptions.frameType.find((opt) => opt.id === configuration.frameType)
    return frameOption ? frameOption.image : "/placeholder.svg?height=300&width=400"
  }

  // Get part image for current configuration
  const getPartImage = (category: string) => {
    const selectedId = configuration[category]
    const option = bikeOptions[category].find((opt) => opt.id === selectedId)
    return option?.partImage || "/placeholder.svg?height=150&width=150"
  }

  // Get current option for a given category
  const getCurrentOption = (category: string) => {
    const selectedId = configuration[category]
    return bikeOptions[category].find((opt) => opt.id === selectedId)
  }

  // Function to move to the next part in the customization flow
  const goToNextPart = () => {
    const currentIndex = partOrder.findIndex((part) => part.key === activeTab)
    if (currentIndex < partOrder.length - 1) {
      setActiveTab(partOrder[currentIndex + 1].key)
      setFocusedPart(partOrder[currentIndex + 1].key)
    }
  }

  // Get the current part description
  const getCurrentPartDescription = () => {
    const part = partOrder.find((p) => p.key === activeTab)
    return part?.description || ""
  }

  // Create configuration details object for cart
  const getConfigDetails = () => {
    const details: { [key: string]: { name: string; price: number } } = {}

    Object.entries(configuration).forEach(([category, selectedId]) => {
      const option = bikeOptions[category]?.find((opt) => opt.id === selectedId)
      if (option) {
        details[category] = {
          name: option.name,
          price: option.price,
        }
      }
    })

    return details
  }

  // Add the bike to cart
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

  return (
    <div className="space-y-8">
      {/* Header with product info if customizing a pre-configured bike */}
      {productName && (
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
            <h2 className="text-2xl font-bold mb-2">Build Your Dream Bike</h2>
            <p className="text-gray-600 mb-4">
              You're customizing the <span className="font-semibold">{productName}</span>. Feel free to modify any
              options to create your perfect ride.
            </p>
            <div className="flex flex-wrap gap-2">
              {Object.entries(configuration).map(([category, value]) => {
                const option = bikeOptions[category]?.find((opt) => opt.id === value)
                if (!option) return null

                return (
                  <Badge key={category} variant="outline" className="bg-white">
                    {option.name}
                  </Badge>
                )
              })}
            </div>
          </div>
        </div>
      )}

      {/* If not customizing a pre-configured bike */}
      {!productName && (
        <div className="bg-white rounded-lg border shadow-sm p-6">
          <h2 className="text-2xl font-bold mb-2">Build Your Dream Bike</h2>
          <p className="text-gray-600">
            Customize every aspect of your bicycle to create the perfect ride for your style and needs. Select from
            premium components and watch your creation come to life.
          </p>
        </div>
      )}

      {/* Main customization area */}
      <div className="grid md:grid-cols-5 gap-8">
        {/* Left side: Bike visualization */}
        <div className="md:col-span-2 bg-white rounded-lg border shadow-sm p-6">
          <div className="bg-gray-50 p-4 rounded-lg mb-6">
            <div className="relative w-full h-[300px] mx-auto">
              <img
                src={getCurrentFrameImage() || "/placeholder.svg"}
                alt={`${configuration.frameType} bike frame`}
                className="object-contain w-full h-full"
              />
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-xl font-semibold">Configuration Summary</h3>
            <ul className="space-y-3">
              {Object.entries(configuration).map(([category, value]) => {
                const option = bikeOptions[category]?.find((opt) => opt.id === value)
                const categoryName = partOrder.find((p) => p.key === category)?.name

                return (
                  <li key={category} className="flex justify-between items-center py-2 border-b">
                    <span className="text-gray-600">{categoryName}</span>
                    <div className="flex items-center">
                      <span className="font-medium mr-4">{option?.name}</span>
                      <span className="text-teal-600 font-semibold">
                        {option?.price ? `$${option.price}` : "Included"}
                      </span>
                    </div>
                  </li>
                )
              })}
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
            {/* Breadcrumb navigation */}
            <TabsList className="w-full grid grid-cols-5 mb-6">
              {partOrder.map((part) => (
                <TabsTrigger
                  key={part.key}
                  value={part.key}
                  onClick={() => {
                    setActiveTab(part.key)
                    setFocusedPart(part.key)
                  }}
                  className={cn(activeTab === part.key ? "border-b-2 border-teal-600" : "")}
                >
                  {part.name}
                </TabsTrigger>
              ))}
            </TabsList>

            {/* Part options */}
            {Object.keys(bikeOptions).map((category) => (
              <TabsContent key={category} value={category} className="pt-4">
                <div className="mb-4 flex justify-between items-center">
                  <div>
                    <h3 className="text-xl font-semibold mb-1">{partOrder.find((p) => p.key === category)?.name}</h3>
                    <p className="text-gray-500">Select your preferred option</p>
                  </div>
                  {category !== partOrder[partOrder.length - 1].key && (
                    <Button onClick={goToNextPart} className="bg-teal-600 hover:bg-teal-700">
                      Next <ChevronRight className="ml-1 h-4 w-4" />
                    </Button>
                  )}
                </div>

                <RadioGroup
                  value={configuration[category]}
                  onValueChange={(value) => handleConfigChange(category, value)}
                  className="grid grid-cols-1 md:grid-cols-3 gap-6"
                >
                  {bikeOptions[category].map((option) => {
                    const compatible = isCompatible(category, option.id)
                    return (
                      <Card
                        key={option.id}
                        className={cn(
                          "relative overflow-hidden transition-all",
                          configuration[category] === option.id ? "ring-2 ring-teal-600" : "border",
                          !compatible ? "opacity-60" : "hover:shadow-md",
                        )}
                      >
                        <div
                          className={cn(
                            "absolute inset-0 z-0",
                            configuration[category] === option.id ? "bg-teal-50" : "bg-transparent",
                          )}
                        />

                        <RadioGroupItem
                          value={option.id}
                          id={`${category}-${option.id}`}
                          className="sr-only peer"
                          disabled={!compatible}
                        />

                        <label
                          htmlFor={`${category}-${option.id}`}
                          className={cn(
                            "flex flex-col h-full cursor-pointer z-10 relative",
                            !compatible && "cursor-not-allowed",
                          )}
                        >
                          <div className="relative h-40 bg-gray-50 border-b">
                            {category === "rimColor" ? (
                              <div className="absolute inset-0 flex items-center justify-center">
                                <div
                                  className="h-20 w-20 rounded-full border-4 border-gray-200"
                                  style={{ backgroundColor: option.color || "#000000" }}
                                />
                              </div>
                            ) : (
                              <img
                                src={option.partImage || "/placeholder.svg"}
                                alt={option.name}
                                className="object-contain p-2 w-full h-full"
                              />
                            )}

                            {configuration[category] === option.id && (
                              <div className="absolute top-2 right-2 bg-teal-600 text-white rounded-full p-1">
                                <Check className="h-4 w-4" />
                              </div>
                            )}
                          </div>

                          <CardContent className="p-4 flex-grow flex flex-col">
                            <div className="flex items-start justify-between mb-2">
                              <h4 className="font-medium text-lg">{option.name}</h4>
                              <span className="text-teal-600 font-semibold">
                                {option.price > 0 ? `+$${option.price}` : "Included"}
                              </span>
                            </div>

                            <p className="text-sm text-gray-500 mb-3 flex-grow">
                              {option.description || "No description available"}
                            </p>

                            {!compatible && (
                              <div className="flex items-center text-amber-600 mt-1 text-sm">
                                <AlertCircle className="h-3 w-3 mr-1" />
                                Not compatible with current configuration
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

