import { useState, useEffect } from "react"
import { useQuery } from "@tanstack/react-query"
import { fetchProductById } from "@client/services/api"

export function useProductConfiguration(productId: string | undefined, categoryId: number | null, parts: any[]) {
  const [configuration, setConfiguration] = useState<{ [key: string]: string }>({})
  const [activeTab, setActiveTab] = useState<string>("")
  
  // Get pre-configured product if productId is provided
  const { 
    data: preConfiguredProduct, 
    isLoading: isLoadingPreConfiguredProduct
  } = useQuery({
    queryKey: ["productById", productId],
    queryFn: () => productId ? fetchProductById(productId) : null,
    enabled: !!productId,
  })

  // Initialize configuration when parts and preConfiguredProduct are available
  useEffect(() => {
    // Only run initialization if we have parts loaded
    if (parts.length === 0) return

    // If preConfiguredProduct is loading, wait for it
    if (productId && isLoadingPreConfiguredProduct) return

    // Now initialize the configuration
    initializeConfiguration()
  }, [parts, preConfiguredProduct, isLoadingPreConfiguredProduct, productId])

  // Update active tab when parts change
  useEffect(() => {
    if (parts.length > 0 && !activeTab) {
      setActiveTab(parts[0].name)
    }
  }, [parts, activeTab])

  // Initialize configuration based on pre-configured product or select first options
  const initializeConfiguration = () => {
    const initialConfig: { [key: string]: string } = {}

    // If we have a preconfigured product, use its configuration
    if (preConfiguredProduct && preConfiguredProduct.parts) {
      // For each part in our available parts
      parts.forEach((part) => {
        // Try to find a matching preconfigured part option
        const preConfiguredPart = preConfiguredProduct.parts.find(
          (p) => {
            // Find the option in our available options that matches the preconfigured part_option
            const matchingOption = part.options.find(
              (opt) => opt.id === p.part_option
            )
            // If we found a matching option for this part, return true
            return matchingOption !== undefined
          }
        )

        // If we found a matching preconfigured part, set it in our configuration
        if (preConfiguredPart) {
          initialConfig[part.name] = preConfiguredPart.part_option.toString()
        }
        // If no preconfigured part was found but we have options, select the first one
        else if (part.options && part.options.length > 0) {
          initialConfig[part.name] = part.options[0].id.toString()
        }
      })
    } else {
      // If creating from scratch, only initialize the first part (if any)
      if (parts.length > 0 && parts[0].options && parts[0].options.length > 0) {
        initialConfig[parts[0].name] = parts[0].options[0].id.toString()
      }
    }

    setConfiguration(initialConfig)
  }

  // Handle configuration change for a part
  const handleConfigChange = (partName: string, optionId: string) => {
    setConfiguration((prev) => ({
      ...prev,
      [partName]: optionId,
    }))
  }

  // Move to next part in the configuration process
  const goToNextPart = () => {
    const currentIndex = parts.findIndex((part) => part.name === activeTab)
    if (currentIndex < parts.length - 1) {
      setActiveTab(parts[currentIndex + 1].name)
    }
  }

  // Get option details for a specific part and option ID
  const getOptionDetails = (partName: string, optionId: string) => {
    const part = parts.find((p) => p.name === partName)
    if (!part) return null

    return part.options.find((opt) => opt.id.toString() === optionId)
  }

  // Get current part description
  const getCurrentPartDescription = () => {
    const part = parts.find((p) => p.name === activeTab)
    const option = part?.options.find((opt) => opt.id.toString() === configuration[part?.name])
    return option?.description || part?.description || ""
  }

  // Get image for a specific option
  const getOptionImage = (partName: string, optionId: string) => {
    const option = getOptionDetails(partName, optionId)
    return option?.image_url || "/placeholder.svg?height=150&width=150"
  }

  // Get image for current active part/option
  const getCurrentImage = () => {
    const activePart = parts.find((p) => p.name === activeTab)
    if (activePart && configuration[activeTab]) {
      const activeOption = activePart.options.find(
        (opt) => opt.id.toString() === configuration[activeTab],
      )
      if (activeOption?.image_url) {
        return activeOption.image_url
      }
    }
    return "/placeholder.svg?height=300&width=400"
  }

  // Check if configuration is complete
  const isConfigurationComplete = () => {
    if (parts.length === 0) return false
    return parts.every(part => configuration[part.name] !== undefined)
  }

  return {
    configuration,
    activeTab,
    preConfiguredProduct,
    isLoadingPreConfiguredProduct,
    setActiveTab,
    handleConfigChange,
    goToNextPart,
    getOptionDetails,
    getCurrentPartDescription,
    getOptionImage,
    getCurrentImage,
    isConfigurationComplete,
  }
}
